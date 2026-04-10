import json
from typing import Dict

import redis
from celery import shared_task

from app.core.config import settings
from app.db.session import SyncSessionLocal
from app.models.enum import NotificationType
from app.models.notification import Notification


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_notification(
    self,
    user_id: str,
    title: str,
    message: str,
    type: NotificationType,
    payload: Dict | None = None,
):
    try:
        run(user_id, title, message, type, payload or {})
    except Exception as exc:
        raise self.retry(exc=exc)


def run(user_id, title, message, type, payload):
    with SyncSessionLocal() as db:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            payload=payload,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

    push_to_redis(
        str(user_id),
        {
            "id": str(notif.id),
            "title": notif.title,
            "message": notif.message,
            "type": notif.type,
            "payload": notif.payload,
        },
    )


def push_to_redis(user_id: str, data: dict):
    r = redis.from_url(settings.redis_url)
    r.publish(f"sse:{user_id}", json.dumps(data))
    r.close()
