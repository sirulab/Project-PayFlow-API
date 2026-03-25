# core/celery_app.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# 預設連線到本地端的 Redis 伺服器
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 初始化 Celery
celery_app = Celery(
    "payflow_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Taipei',
    enable_utc=True,
)