from celery import Celery
from app.config import settings

celery_app = Celery(
    "vendornest",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.delivery_sync", "app.tasks.notifications"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "sync-delhivery-every-30min": {
            "task": "sync_delhivery_status",
            "schedule": 1800.0,  # every 30 minutes
        },
    },
)
