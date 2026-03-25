from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_session
from .models import Order
from features.products.models import Product
from features.payments.ecpay_service import create_ecpay_params

router = APIRouter(prefix="/orders", tags=["Orders"])

# 移除 response_class=HTMLResponse，改為預設的 JSON
@router.post("/")
async def create_order(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product or product.stock <= 0:
        raise HTTPException(status_code=400, detail="庫存不足")
    
    new_order = Order(product_id=product_id, amount=product.price)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    # 取得綠界需要的參數
    ecpay_data = create_ecpay_params(new_order.id, new_order.amount, product.name)
    payment_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    
    # 直接回傳 JSON 讓前端 (或測試者) 知道要把這些資料 POST 去哪裡
    return {
        "message": "訂單建立成功",
        "order_id": new_order.id,
        "payment_info": {
            "submit_url": payment_url,
            "method": "POST",
            "form_data": ecpay_data
        }
    }