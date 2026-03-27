import json
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.config import settings

log = structlog.get_logger()
router = APIRouter()

# Channel prefix for pub/sub
CHANNEL_PREFIX = "research:progress:"


@router.websocket("/ws/research/{task_id}")
async def research_progress_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()

    channel = f"{CHANNEL_PREFIX}{task_id}"
    await pubsub.subscribe(channel)
    log.info("ws_subscribed", task_id=task_id, channel=channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        log.info("ws_disconnected", task_id=task_id)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await redis.aclose()


async def publish_event(redis_url: str, task_id: str, event: dict) -> None:
    """Publish a progress event from Celery workers."""
    redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        event["task_id"] = task_id
        channel = f"{CHANNEL_PREFIX}{task_id}"
        await redis.publish(channel, json.dumps(event))
    finally:
        await redis.aclose()
