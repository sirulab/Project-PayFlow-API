# features/payments/router.py
from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from core.database import get_session

# 移除舊的 event_bus
# from core.event_bus import event_bus 

from features.orders.models import Order
from .ecpay_service import verify_ecpay_checksum
from features.payments.tasks import process_payment_success_task # 引入 Celery Task

router = APIRouter(tags=["Payments"])

@router.post("/webhooks/ecpay")
async def ecpay_webhook(request: Request, session: Session = Depends(get_session)):
    form_data = await request.form()
    payload = dict(form_data)
    
    if not verify_ecpay_checksum(payload):
        return "0|CheckMacValue Error"

    order_id = int(payload.get("CustomField1", 0))
    rtn_code = payload.get("RtnCode")
    is_simulate = payload.get("SimulatePaid") == "1"

    if is_simulate:
        return "1|OK"

    if rtn_code == "1":
        order = session.get(Order, order_id)
        
        if order and order.status == "pending":
            order.status = "paid"
            session.add(order)
            session.commit()
            
            # 🔴 核心亮點：將「扣庫存與寄信」這件耗時任務，丟入 Redis 佇列，讓 API 瞬間回傳 1|OK 給綠界
            process_payment_success_task.delay(order.id)
            print(f" [成功] 訂單 {order_id} 付款完成，已推送任務至 Celery Redis Broker。")
            
    return "1|OK"