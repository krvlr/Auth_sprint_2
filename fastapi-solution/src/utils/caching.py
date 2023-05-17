import logging
from functools import wraps
from typing import Callable

from core.config import settings
from db.base_cache import CacheAdapter
from db.cache_adapter import get_redis_adapter

logger = logging.getLogger(__name__)


def cache(
    expire: int = settings.cache_expire_in_seconds,
    cache_adapter: CacheAdapter = get_redis_adapter(),
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_adapter.generate_key(func, *args, **kwargs)
            cache_data = await cache_adapter.get(cache_key, expire)
            if cache_data is not None:
                return cache_data
            else:
                data = await func(*args, **kwargs)
                if data is None:
                    return None
                await cache_adapter.set(cache_key, data)
                return data

        return wrapper

    return decorator
