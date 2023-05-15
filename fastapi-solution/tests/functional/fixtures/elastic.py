import json
from http import HTTPStatus
from typing import Iterable

import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from settings import test_settings
from testdata.schemes.es_schema import INDEXES


async def _create_indexes(es_client: AsyncElasticsearch) -> None:
    for index_name, index_params in INDEXES.items():
        await es_client.indices.create(
            index=index_name, ignore=HTTPStatus.BAD_REQUEST, body=index_params
        )


async def _delete_indexes(es_client: AsyncElasticsearch) -> None:
    for index_name, _ in INDEXES.items():
        await es_client.indices.delete(index=index_name)


@pytest_asyncio.fixture(scope="function")
async def es_client() -> AsyncElasticsearch:
    url_elastic = f"{test_settings.elastic_host}:{test_settings.elastic_port}"
    client = AsyncElasticsearch(url_elastic, validate_cert=False, use_ssl=False)
    await _create_indexes(client)
    yield client
    await _delete_indexes(client)
    await client.close()


def _get_es_bulk_query(es_index: str, es_data: Iterable[dict]) -> str:
    bulk_query = []
    for row in es_data:
        bulk_query.extend(
            [
                json.dumps({"index": {"_index": es_index, "_id": row["id"]}}),
                json.dumps(row),
            ]
        )
    return "\n".join(bulk_query) + "\n"


@pytest_asyncio.fixture(scope="function")
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(es_index: str, data: Iterable[dict]) -> None:
        bulk_query = _get_es_bulk_query(es_index, data)
        response = await es_client.bulk(bulk_query, refresh=True)
        if response["errors"]:
            raise Exception(f"Ошибка записи данных в Elasticsearch")

    return inner
