import logging
from functools import lru_cache

from db.base_db import DataProvider, DbAdapter, ObjectName
from db.elastic import get_elastic_data_provider
from db.elastic_adapter import ElasticAdapter
from fastapi import Depends
from models.genre import GenreBrief, GenreDetail
from utils.caching import cache

logger = logging.getLogger(__name__)


class GenreService:
    def __init__(self, db_adapter: DbAdapter):
        self.db_adapter = db_adapter

    @cache()
    async def get_by_id(self, obj_id: str, model_cls=GenreDetail) -> GenreDetail | None:
        return await self.db_adapter.get_object_by_id(obj_id, ObjectName.GENRES, model_cls)

    @cache()
    async def get_list(
        self,
        sort: list[str] | None,
        page_number: int,
        page_size: int,
        filters: dict,
    ) -> list[GenreBrief]:
        return await self.db_adapter.search(
            obj_name=ObjectName.GENRES,
            model=GenreBrief,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
        )


@lru_cache()
def get_genre_service(
    data_provider: DataProvider = Depends(get_elastic_data_provider),
) -> GenreService:
    elastic_adapter = ElasticAdapter(
        data_provider=data_provider,
        allowed_sort_fields={"name": str, "description": str},
    )
    genre_service = GenreService(db_adapter=elastic_adapter)
    return genre_service
