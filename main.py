from fastapi import FastAPI
import asyncio
from core.database import create_db_and_tables
from features.products.router import router as product_router
from features.orders.router import router as order_router
from features.payments.router import router as payment_router
from features.payments.event_handlers import event_worker

app = FastAPI(title="PayFlow API - HTMX Version")

# 註冊路由
app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)

@app.on_event("startup")
def startup():
    create_db_and_tables()
    asyncio.create_task(event_worker())