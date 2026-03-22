import asyncio
import json
from typing import Dict, Sequence

from fastapi.responses import StreamingResponse
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enum import NotificationType
from app.models.notification import Notification
from app.tasks.notifications import send_notification


async def notification_generator(user_id: int):
    async def generator():
        r = await Redis.from_url(settings.redis_url)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"sse:{user_id}")
        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=20
                )
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    yield f"event: notification\ndata: {json.dumps(data)}\nid: {data.get('id', '')}\n\n"
                else:
                    yield ": ping\n\n"
                    await asyncio.sleep(1)
        except asyncio.CancelledError, GeneratorExit:
            pass
        finally:
            await pubsub.unsubscribe(f"sse:{user_id}")
            await r.aclose()

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def fetch_notifications(
    user_id: int,
    db: AsyncSession,
    unread_only: bool = False,
) -> Sequence[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    result = await db.execute(q.order_by(Notification.created_at.desc()).limit(50))
    return result.scalars().all()


async def mark_all_read(user_id: int, db: AsyncSession) -> Dict:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "Successfull"}


def notify(
    user_id: str,
    title: str,
    message: str,
    type: NotificationType,
    payload: dict | None = None,
) -> None:
    send_notification.delay(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        payload=payload,
    )
