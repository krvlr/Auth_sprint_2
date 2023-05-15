import abc
import logging
from abc import ABCMeta
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CacheProvider(metaclass=ABCMeta):
    @abc.abstractmethod
    async def get(
        self,
        name: str,
    ):
        pass

    @abc.abstractmethod
    async def set(self, name: str, value: object):
        pass


class CacheAdapter(metaclass=ABCMeta):
    @abc.abstractmethod
    def __init__(self, cache_provider: CacheProvider):
        self.cache_provider = cache_provider

    @staticmethod
    @abc.abstractmethod
    def generate_key(func: Callable, *args, **kwargs):
        """Method for generate cache key."""
        pass

    @abc.abstractmethod
    async def set(self, cache_key: str, data: Any):
        """Method for save data in cache."""
        pass

    @abc.abstractmethod
    async def get(self, cache_key: str, expire: int):
        """Method for load data in cache."""
        pass
