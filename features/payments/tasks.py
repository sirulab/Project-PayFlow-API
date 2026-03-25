# features/payments/tasks.py
from sqlmodel import Session, select
from core.database import engine
from core.email import send_email_notification
from features.orders.models import Order
from features.products.models import Product
from core.celery_app import celery_app
import asyncio

# 🔴 核心亮點：註冊為 Celery 背景任務
@celery_app.task(name="process_payment_success")
def process_payment_success_task(order_id: int):
    with Session(engine) as session:
        order = session.get(Order, order_id)
        if not order: 
            return f"找不到訂單 {order_id}"
        
        # 結合上一步的 Exclusive Lock
        statement = select(Product).where(Product.id == order.product_id).with_for_update()
        product = session.exec(statement).first()
        
        if product and product.stock > 0:
            product.stock -= 1
            session.add(product)
            session.commit()
            print(f" [Celery Worker] {product.name} 剩餘庫存 {product.stock}")
            
            # Celery 預設是同步執行的，但我們的寄信模組是 async (aiosmtplib)
            # 因此使用 asyncio.run() 在任務中啟動事件迴圈來寄信
            asyncio.run(send_email_notification(order.id, order.amount))
            return f"訂單 {order_id} 處理成功"
        else:
            session.rollback()
            print(f" [Celery Worker 警告] 訂單 {order_id} 庫存不足，需進行退款。")
            return f"訂單 {order_id} 處理失敗：庫存不足"