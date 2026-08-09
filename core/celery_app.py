from celery import Celery

redis_url = "redis://redis:6379/0" 

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
