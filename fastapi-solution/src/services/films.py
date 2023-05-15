import logging
from functools import lru_cache

from db.base_db import DataProvider, DbAdapter, ObjectName
from db.elastic import get_elastic_data_provider
from db.elastic_adapter import ElasticAdapter
from fastapi import Depends
from models.film import FilmBrief, FilmDetail
from utils.caching import cache

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, db_adapter: DbAdapter):
        self.db_adapter = db_adapter

    @cache()
    async def get_by_id(self, obj_id: str, model_cls=FilmDetail) -> FilmDetail | None:
        return await self.db_adapter.get_object_by_id(
            obj_id=obj_id, obj_name=ObjectName.MOVIES, model_cls=model_cls
        )

    @cache()
    async def get_list(
        self, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[FilmBrief]:
        return await self.db_adapter.search(
            obj_name=ObjectName.MOVIES,
            model=FilmDetail,
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
    ) -> list[FilmDetail]:
        return await self.db_adapter.search(
            obj_name=ObjectName.MOVIES,
            model=FilmDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
            query=query,
        )


@lru_cache()
def get_film_service(
    data_provider: DataProvider = Depends(get_elastic_data_provider),
) -> FilmService:
    elastic_adapter = ElasticAdapter(
        data_provider=data_provider,
        allowed_sort_fields={"title": str, "imdb_rating": float},
    )
    film_service = FilmService(db_adapter=elastic_adapter)
    return film_service
