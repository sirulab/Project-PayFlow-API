from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from core.database import get_session
from core.event_bus import event_bus
from features.orders.models import Order
from .ecpay_service import verify_ecpay_checksum

# 定義 router 供 main.py 匯入
router = APIRouter(tags=["Payments"])

@router.post("/webhooks/ecpay")
async def ecpay_webhook(request: Request, session: Session = Depends(get_session)):
    # 綠界 Webhook 回傳的是 Form Data，需要 python-multipart
    form_data = await request.form()
    payload = dict(form_data)
    
    # 1. 驗證簽章是否正確
    if not verify_ecpay_checksum(payload):
        print(" [失敗] 簽章驗證失敗")
        return "0|CheckMacValue Error"

    # 2. 解析回傳參數
    order_id = int(payload.get("CustomField1", 0))
    rtn_code = payload.get("RtnCode")
    is_simulate = payload.get("SimulatePaid") == "1"

    # 模擬付款 (綠界後台手動觸發測試時，不進行後續庫存扣除)
    if is_simulate:
        print(f" [成功] order_id {order_id} 模擬付款成功，不觸發後續動作 ")
        return "1|OK"

    # 3. 處理真實付款成功 (RtnCode == "1")
    if rtn_code == "1":
        order = session.get(Order, order_id)
        
        # 檢查訂單狀態避免重複處理 (Idempotency)
        if order and order.status == "pending":
            order.status = "paid"
            session.add(order)
            session.commit()
            
            # 將成功事件發布到 EventBus，讓 event_worker 異步處理寄信與扣庫存
            await event_bus.publish({"event": "PAYMENT_SUCCESS", "order_id": order.id})
            print(f" [成功] 訂單 {order_id} 付款完成，已發送背景處理事件。")
            
    return "1|OK"