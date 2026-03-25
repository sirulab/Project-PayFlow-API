from sqlmodel import Session
from core.database import engine
from core.event_bus import event_bus
from core.email import send_email_notification
from features.orders.models import Order
from features.products.models import Product
import asyncio

async def event_worker():
    async for event in event_bus.subscribe():
        if event.get("event") == "PAYMENT_SUCCESS":
            order_id = event.get("order_id")
            with Session(engine) as session:
                order = session.get(Order, order_id)
                if not order: continue
                
                product = session.get(Product, order.product_id)
                if product and product.stock > 0:
                    product.stock -= 1
                    session.add(product)
                    session.commit()
                    print(f" [更新] {product.name} 剩餘庫存 {product.stock}")
                    asyncio.create_task(send_email_notification(order.id, order.amount))
        await asyncio.sleep(0.1)