from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import create_db_and_tables
from features.products.router import router as product_router
from features.orders.router import router as order_router
from features.payments.router import router as payment_router

# Lifespan 管理啟動與關閉事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# lifespan 綁定到 FastAPI 實例
app = FastAPI(title="PayFlow API", lifespan=lifespan)

# 註冊路由
app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)
