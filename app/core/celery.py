from celery import Celery

from app.core.config import settings

print(f"DEBUG: Celery is trying to use Broker URL: '{settings.redis_url}'")

worker_celery_app = Celery(
    "my background app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.images", "app.tasks.notifications"],
)
