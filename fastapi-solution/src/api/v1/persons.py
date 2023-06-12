import logging
from dataclasses import asdict
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from models.person import PersonBrief, PersonDetail, PersonFilters
from models.shared import Paginator
from services.auth import JWTBearerPremium
from services.persons import PersonService, get_person_service

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/search", response_model=list[PersonBrief])
async def person_search(
    query: str | None = None,
    sort: list[str] | None = Query(default=None),
    filters: PersonFilters = Depends(PersonFilters),
    paginator: Paginator = Depends(Paginator),
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonBrief]:
    return await person_service.get_by_query(
        query, sort, paginator.page_number, paginator.page_size, asdict(filters)
    )


@router.get("/", response_model=list[PersonBrief])
async def person_list(
    sort: list[str] | None = Query(default=None),
    filters: PersonFilters = Depends(PersonFilters),
    paginator: Paginator = Depends(Paginator),
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonBrief]:
    return await person_service.get_list(
        sort, paginator.page_number, paginator.page_size, asdict(filters)
    )


@router.get("/{person_id}", dependencies=[Depends(JWTBearerPremium())], response_model=PersonDetail)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonDetail:
    person = await person_service.get_by_id(person_id, model_cls=PersonDetail)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person
