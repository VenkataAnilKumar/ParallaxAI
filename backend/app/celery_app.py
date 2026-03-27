from celery import Celery

from app.config import settings

celery_app = Celery(
    "parallax",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.research"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,  # 24 hours
    task_routes={
        "app.tasks.research.*": {"queue": "research"},
    },
    task_time_limit=600,       # 10 min hard limit
    task_soft_time_limit=540,  # 9 min soft limit (allows cleanup)
)
