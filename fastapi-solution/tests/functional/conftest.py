import pytest_asyncio
from aiohttp import ClientSession

from .settings import test_settings

pytest_plugins = ["fixtures.elastic", "fixtures.redis"]


@pytest_asyncio.fixture(scope="function")
async def session():
    session = ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="function")
def make_get_request(session, redis_client):
    async def inner(endpoint: str, params: dict = None, flush_cache=True) -> (int, dict):
        if flush_cache:
            await redis_client.flushall()

        url = f"{test_settings.api_url}/{endpoint}"
        async with session.get(url, params=params) as response:
            return response.status, await response.json()

    return inner
