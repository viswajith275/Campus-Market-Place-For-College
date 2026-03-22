import asyncio
import json
from collections import defaultdict

from redis.asyncio import Redis

from app.core.config import settings


class SSEManager:
    def __init__(self):
        self._queues: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._redis = None

    async def get_redis(self):
        if not self._redis:
            self._redis = await Redis.from_url(settings.redis_url)
        return self._redis

    def subscribe(self, user_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self._queues[user_id].add(q)
        return q

    def unsubscribe(self, user_id: str, q: asyncio.Queue):
        self._queues[user_id].discard(q)

    async def send(self, user_id: str, data: dict):
        # push to all local queues (called by FastAPI process)
        for q in self._queues.get(user_id, set()):
            await q.put(data)

    async def publish(self, user_id: str, data: dict):
        # called by Celery — publishes to Redis channel
        r = await self.get_redis()
        await r.publish(f"sse:{user_id}", json.dumps(data))

    async def listen(self, user_id: str):
        # run this on startup to forward Redis messages into local queues
        r = await Redis.from_url(settings.redis_url)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"sse:{user_id}")
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await self.send(user_id, data)


manager = SSEManager()
