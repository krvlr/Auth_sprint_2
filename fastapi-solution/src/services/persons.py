import logging
from functools import lru_cache

from db.base_db import DataProvider, DbAdapter, ObjectName
from db.elastic import get_elastic_data_provider
from db.elastic_adapter import ElasticAdapter
from fastapi import Depends
from models.person import PersonBrief, PersonDetail
from utils.caching import cache

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, db_adapter: DbAdapter):
        self.db_adapter = db_adapter

    @cache()
    async def get_by_id(self, obj_id: str, model_cls=PersonDetail) -> PersonDetail | None:
        return await self.db_adapter.get_object_by_id(obj_id, ObjectName.PERSONS, model_cls)

    @cache()
    async def get_list(
        self, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[PersonBrief]:
        return await self.db_adapter.search(
            obj_name=ObjectName.PERSONS,
            model=PersonDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
        )

    async def get_by_query(
        self,
        query: str,
        sort: list[str] | None,
        page_number: int,
        page_size: int,
        filters: dict,
    ) -> list[PersonDetail]:
        return await self.db_adapter.search(
            obj_name=ObjectName.PERSONS,
            model=PersonDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
            query=query,
        )


@lru_cache()
def get_person_service(
    data_provider: DataProvider = Depends(get_elastic_data_provider),
) -> PersonService:
    elastic_adapter = ElasticAdapter(
        data_provider=data_provider,
        allowed_sort_fields={"full_name": str},
    )
    person_service = PersonService(db_adapter=elastic_adapter)
    return person_service
