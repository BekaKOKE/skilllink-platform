from celery import Celery
from celery.schedules import crontab

from backend.app.core.config import settings

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

celery_app = Celery(
    "skilllink",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "backend.app.tasks.email_tasks",
        "backend.app.tasks.image_tasks",
        "backend.app.tasks.order_tasks"
    ],
)
celery_app.conf.beat_schedule = {
    "cancel-expired-orders": {
        "task": "tasks.cancel_expired_orders",
        "schedule": 10.0,
    }
}

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)