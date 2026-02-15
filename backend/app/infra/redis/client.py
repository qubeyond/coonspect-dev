from redis import asyncio as aioredis

from app.common.settings import settings

redis_client = aioredis.from_url(
    str(settings.redis_url), encoding="utf-8", decode_responses=True
)  # type: ignore[no-untyped-call]
