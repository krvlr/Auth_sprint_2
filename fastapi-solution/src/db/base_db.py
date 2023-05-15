import abc
import logging
from abc import ABCMeta
from enum import Enum
from typing import Type

from models.film import FilmBrief, FilmDetail
from models.genre import GenreBrief, GenreDetail
from models.person import PersonBrief, PersonDetail
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SortingOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class ObjectName(Enum):
    MOVIES = "movies"
    GENRES = "genres"
    PERSONS = "persons"


class DataProvider(metaclass=ABCMeta):
    @abc.abstractmethod
    async def get(self, obj_name: str, obj_id: str):
        pass

    @abc.abstractmethod
    async def search(self, obj_name, body, from_, size, sort):
        pass


class DbAdapter(metaclass=ABCMeta):
    @abc.abstractmethod
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    @abc.abstractmethod
    async def get_object_by_id(
        self,
        obj_id: str,
        obj_name: ObjectName,
        model_cls: Type[FilmDetail | GenreDetail | PersonDetail],
    ) -> BaseModel | None:
        pass

    @abc.abstractmethod
    async def search(
        self,
        obj_name: ObjectName,
        model: Type[FilmBrief | GenreBrief | PersonBrief],
        sort: list[str] | None,
        page_number: int,
        page_size: int,
        filters: dict[str, list | None],
        query: tuple[str, str] | None = None,
    ) -> list[BaseModel] | list:
        pass
