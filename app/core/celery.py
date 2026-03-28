from celery import Celery

from app.core.config import settings

worker_celery_app = Celery(
    "my background app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.images", "app.tasks.notifications"],
)
