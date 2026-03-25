# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import create_db_and_tables
from features.products.router import router as product_router
from features.orders.router import router as order_router
from features.payments.router import router as payment_router

# 使用最新的 Lifespan 管理啟動與關閉事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 伺服器啟動時執行的動作 (Startup)
    create_db_and_tables()
    yield
    # 伺服器關閉時執行的動作 (Shutdown) 可以寫在 yield 之後

# 將 lifespan 綁定到 FastAPI 實例上
app = FastAPI(title="PayFlow API", lifespan=lifespan)

# 註冊路由
app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)