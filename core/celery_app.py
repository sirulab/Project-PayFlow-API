from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    "payflow_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["features.payments.tasks"]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Taipei',
    enable_utc=True,
)
