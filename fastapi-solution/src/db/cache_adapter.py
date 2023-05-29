from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from inspect import signature

from redis.asyncio import Redis
from typing import Any, Callable

from core.config import settings
from db.base_cache import CacheAdapter, CacheProvider
from db.redis import RedisProvider
from utils.cache_serializer import PickleCacheSerializer


@dataclass
class CacheData:
    saved_datetime: datetime
    data: Any


class RedisAdapter(CacheAdapter):
    def __init__(self, cache_provider: CacheProvider):
        self.cache_provider = cache_provider

    @staticmethod
    def generate_key(func: Callable, *args, **kwargs) -> str:
        """Method for generate cache key."""
        func_args = signature(func).bind(*args, **kwargs)
        func_args.apply_defaults()

        func_args_str = ",".join(
            f"{arg}={val}" for arg, val in func_args.arguments.items() if arg != "self"
        )

        return f"={func.__qualname__}.({func_args_str})"

    async def set(self, cache_key: str, data: Any) -> Any:
        """Method for save data in cache."""
        cache_data = CacheData(saved_datetime=datetime.now(), data=data)
        await self.cache_provider.set(cache_key, PickleCacheSerializer.serialize(cache_data))

    async def get(self, cache_key: str, expire: int) -> Any:
        """Method for load data in cache."""
        cache_data = await self.cache_provider.get(cache_key)
        if cache_data:
            cache_data = PickleCacheSerializer.deserialize(cache_data)
            if (datetime.now() - cache_data.saved_datetime).seconds < expire:
                return cache_data.data
            else:
                return None


@lru_cache()
def get_redis_adapter() -> CacheAdapter:
    redis = Redis(host=settings.redis_host, port=settings.redis_port)
    cache_provider = RedisProvider(redis=redis)
    cache_adapter = RedisAdapter(cache_provider=cache_provider)
    return cache_adapter
