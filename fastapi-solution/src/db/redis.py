from typing import Optional

from db.base_cache import CacheProvider
from redis.asyncio.client import Redis

redis: Optional[Redis] = None


class RedisProvider(CacheProvider):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(
        self,
        name: str,
    ):
        return await self.redis.get(name=name)

    async def set(self, name: str, value: object):
        await self.redis.set(name=name, value=value)


def get_redis_cache_provider() -> RedisProvider:
    return RedisProvider(redis=redis)
