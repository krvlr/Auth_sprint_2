from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Union

from redis import Redis


class TokenStorageProvider(ABC):
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value: Any, delta_expire: Union[int, timedelta]):
        pass

    @abstractmethod
    def update(self, key: str, value: Any):
        pass

    @abstractmethod
    def search(self, pattern: str):
        pass


class TokenStorageRedisProvider(TokenStorageProvider):
    def __init__(self, redis: Redis):
        self.redis = redis

    def get(self, key: str) -> Any:
        value = self.redis.get(name=key)
        if value:
            return value.decode()

    def set(self, key: str, value: Any, delta_expire: Union[int, timedelta]):
        self.redis.setex(name=key, time=delta_expire, value=value)

    def update(self, key: str, value: Any):
        self.redis.set(name=key, value=value, xx=True, keepttl=True)

    def search(self, pattern: str):
        return self.redis.scan_iter(match=pattern)
