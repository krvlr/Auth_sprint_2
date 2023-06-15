from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from functools import lru_cache
from typing import Union

from core.config import redis_settings
from db.token_storage_provider import TokenStorageProvider, TokenStorageRedisProvider
from redis import Redis


class TokenStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    NOT_FOUND = None


class TokenStorageAdapter(ABC):
    @abstractmethod
    def __init__(self, token_storage_provider: TokenStorageProvider):
        self.token_storage_provider = token_storage_provider

    @abstractmethod
    def create(self, user_id: str, jti: str, delta_expire: Union[int, timedelta]):
        pass

    @abstractmethod
    def get_status(self, user_id: str, jti: str) -> TokenStatus:
        pass

    @abstractmethod
    def block(self, user_id: str, jti: str):
        pass

    @abstractmethod
    def block_for_pattern(self, pattern: str):
        pass


class TokenStorageRedisAdapter(TokenStorageAdapter):
    def __init__(self, token_storage_provider: TokenStorageProvider):
        super().__init__(token_storage_provider)

    @staticmethod
    def _generate_key(user_id: str, jti: str):
        return f"{user_id}:{jti}"

    def create(self, user_id: str, jti: str, delta_expire: Union[int, timedelta]):
        self.token_storage_provider.set(
            key=self._generate_key(user_id, jti),
            value=TokenStatus.ACTIVE.value,
            delta_expire=delta_expire,
        )

    def get_status(self, user_id: str, jti: str) -> TokenStatus:
        return TokenStatus(self.token_storage_provider.get(key=f"{user_id}:{jti}"))

    def block(self, user_id: str, jti: str):
        self.token_storage_provider.update(
            key=self._generate_key(user_id, jti),
            value=TokenStatus.BLOCKED.value,
        )

    def block_for_pattern(self, pattern: str):
        for key in self.token_storage_provider.search(pattern=pattern):
            self.token_storage_provider.update(
                key=key,
                value=TokenStatus.BLOCKED.value,
            )


@lru_cache()
def get_redis_adapter() -> TokenStorageRedisAdapter:
    redis = Redis(host=redis_settings.host, port=redis_settings.port)
    redis_provider = TokenStorageRedisProvider(redis=redis)
    redis_adapter = TokenStorageRedisAdapter(token_storage_provider=redis_provider)
    return redis_adapter
