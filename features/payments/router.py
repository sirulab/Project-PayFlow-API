from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from core.database import get_session

from features.orders.models import Order
from .ecpay_service import verify_ecpay_checksum
from features.payments.tasks import process_payment_success_task # 引入 Celery Task

router = APIRouter(tags=["Payments"])

@router.post("/webhooks/ecpay")
async def ecpay_webhook(request: Request, session: Session = Depends(get_session)):
    form_data = await request.form()
    payload = dict(form_data)
    
    if not verify_ecpay_checksum(payload):
        print("簽章驗證失敗")
        return "0|CheckMacValue Error"

    order_id = int(payload.get("CustomField1", 0))
    rtn_code = payload.get("RtnCode")
    is_simulate = payload.get("SimulatePaid") == "1"

    if is_simulate:
        return "1|OK"

    if rtn_code == "1":
        order = session.get(Order, order_id)
        print(f"資料庫查詢狀態 - 訂單: {order}, 狀態: {order.status if order else '找不到'}")
        
        if order and order.status == "pending":
            order.status = "paid"
            session.add(order)
            session.commit()
            
            process_payment_success_task.delay(order.id)
            print(f" [成功] 訂單 {order_id} 付款完成，已推送任務至 Celery Redis Broker。")
        else:                                                                       # 👉 新增這行
            print("❌ 條件不符！沒有觸發寄信 (可能是狀態不是 pending)")
            
    return "1|OK"
