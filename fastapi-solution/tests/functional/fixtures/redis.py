import pytest_asyncio
from redis.asyncio.client import Redis
from settings import test_settings


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis
    await redis.close()
