import pytest_asyncio
from redis.asyncio.client import Redis
from settings import redis_settings


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    redis = Redis(host=redis_settings.host, port=redis_settings.port)
    yield redis
    await redis.close()
