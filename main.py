# main.py
from fastapi import FastAPI
from core.database import create_db_and_tables
from features.products.router import router as product_router
from features.orders.router import router as order_router
from features.payments.router import router as payment_router

app = FastAPI(title="PayFlow API")

app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)

@app.on_event("startup")
def startup():
    create_db_and_tables()
    # 已經不需要在這裡 create_task(event_worker()) 了，因為任務現在歸 Celery 管