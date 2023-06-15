from typing import Optional

from db.base_db import DataProvider
from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


class ElasticDataProvider(DataProvider):
    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    async def get(self, obj_name: str, obj_id: str):
        return await self.es.get(index=obj_name, id=obj_id)

    async def search(self, obj_name, body, from_, size, sort):
        return await self.es.search(index=obj_name, body=body, from_=from_, size=size, sort=sort)


async def get_elastic_data_provider() -> ElasticDataProvider:
    return ElasticDataProvider(es=es)
