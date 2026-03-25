from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from core.database import get_session
from .models import Order
from features.products.models import Product
from features.payments.ecpay_service import create_ecpay_params

router = APIRouter(prefix="/orders", tags=["Orders"])
templates = Jinja2Templates(directory="templates")

@router.post("/", response_class=HTMLResponse)
async def create_order(request: Request, product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product or product.stock <= 0:
        raise HTTPException(status_code=400, detail="庫存不足")
    
    new_order = Order(product_id=product_id, amount=product.price)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    ecpay_data = create_ecpay_params(new_order.id, new_order.amount, product.name)
    payment_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    
    return templates.TemplateResponse("payment_redirect.html", {
        "request": request,
        "payment_url": payment_url,
        "ecpay_data": ecpay_data
    })