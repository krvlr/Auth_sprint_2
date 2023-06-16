import json
from dataclasses import dataclass

import pytest_asyncio
from aiohttp import ClientSession

from .settings import auth_api_settings

pytest_plugins = ["fixtures.redis", "fixtures.postgre"]


@dataclass
class HttpResponse:
    status: int
    headers: dict
    cookies: dict
    body: dict


@pytest_asyncio.fixture(scope="function")
async def session():
    session = ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="function")
def make_get_request(session, redis_client):
    async def inner(endpoint: str, token: str = None, flush_cache: bool = True) -> HttpResponse:
        if flush_cache:
            await redis_client.flushall()

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-Id": "authtestrequestid000000000000000",
        }
        url = f"{auth_api_settings.get_api_uri()}/{endpoint}"

        async with session.get(url, headers=headers) as response:
            body = await response.read()
            return HttpResponse(
                status=response.status,
                headers=response.headers,
                cookies=response.cookies,
                body=json.loads(body),
            )

    return inner


@pytest_asyncio.fixture(scope="function")
def make_post_request(session, redis_client):
    async def inner(
        endpoint: str, data: dict = None, token: str = None, flush_cache: bool = True
    ) -> HttpResponse:
        if flush_cache:
            await redis_client.flushall()

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-Id": "authtestrequestid000000000000000",
        }
        url = f"{auth_api_settings.get_api_uri()}/{endpoint}"

        async with session.post(url, json=data if data else dict(), headers=headers) as response:
            body = await response.read()
            return HttpResponse(
                status=response.status,
                headers=response.headers,
                cookies=response.cookies,
                body=json.loads(body),
            )

    return inner
