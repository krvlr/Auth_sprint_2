import random
import string
import uuid
from http import HTTPStatus

import pytest


async def test_genre_by_id_not_found(make_get_request):
    status, response = await make_get_request(f"genres/{0}")
    assert status == HTTPStatus.NOT_FOUND
    assert response == {"detail": "genre not found"}


@pytest.mark.parametrize(
    "id, es_data, expected_answer",
    [
        (
            "ced104fa-d6b3-11ed-afa1-0242ac120002",
            (
                {
                    "id": "ced104fa-d6b3-11ed-afa1-0242ac120002",
                    "name": "Action",
                    "description": "Fast-paced and include a lot of action like fight scenes, "
                    "chase scenes, and slow-motion shots",
                },
            ),
            {
                "id": "ced104fa-d6b3-11ed-afa1-0242ac120002",
                "name": "Action",
                "description": "Fast-paced and include a lot of action like fight scenes, "
                "chase scenes, and slow-motion shots",
            },
        ),
    ],
)
async def test_genre_by_id(
    es_write_data,
    make_get_request,
    id: str,
    es_data: dict,
    expected_answer: dict,
):
    await es_write_data("genres", es_data)

    status, response = await make_get_request(f"genres/{id}")
    assert status == HTTPStatus.OK
    assert response == expected_answer


async def test_genre_empty_list(make_get_request):
    status, response = await make_get_request("genres/")
    assert status == HTTPStatus.OK
    assert len(response) == 0


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "name": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                }
                for _ in range(0, 10)
            ),
            10,
        ),
    ],
)
async def test_genre_cache(
    redis_client,
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("genres", es_data)
    await redis_client.flushall()
    keys = await redis_client.keys(pattern="*")

    assert len(keys) == 0

    status, response = await make_get_request("genres/", flush_cache=False)
    keys = await redis_client.keys(pattern="*")

    assert status == HTTPStatus.OK
    assert len(keys) == 1
    assert len(response) == expected_answer


@pytest.mark.parametrize(
    "page_number, page_size, es_data, expected_answer",
    [
        (
            3,
            2,
            (
                {
                    "id": str(i),
                    "name": str(i),
                }
                for i in range(0, 10)
            ),
            [
                {
                    "id": "4",
                    "name": "4",
                },
                {
                    "id": "5",
                    "name": "5",
                },
            ],
        ),
    ],
)
async def test_genre_pagination(
    es_write_data,
    make_get_request,
    page_number,
    page_size,
    es_data,
    expected_answer,
):
    await es_write_data("genres", es_data)

    status, response = await make_get_request(
        "genres/",
        params={"page_number": page_number, "page_size": page_size, "sort": "name"},
    )

    assert status == HTTPStatus.NOT_FOUND
    assert response == expected_answer


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": "c22ea5ae-e027-11ed-b5ea-0242ac120002",
                    "name": "Comedy",
                },
                {
                    "id": "bca615b8-e027-11ed-b5ea-0242ac120002",
                    "name": "Horror",
                },
                {
                    "id": "6b8d0498-e027-11ed-b5ea-0242ac120002",
                    "name": "Action",
                },
            ),
            [
                {
                    "id": "6b8d0498-e027-11ed-b5ea-0242ac120002",
                    "name": "Action",
                },
                {
                    "id": "c22ea5ae-e027-11ed-b5ea-0242ac120002",
                    "name": "Comedy",
                },
                {
                    "id": "bca615b8-e027-11ed-b5ea-0242ac120002",
                    "name": "Horror",
                },
            ],
        ),
    ],
)
async def test_genre_sorting(
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("genres", es_data)

    status, response = await make_get_request("genres/", params={"sort": "name"})

    assert status == HTTPStatus.NOT_FOUND
    assert response == expected_answer


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "name": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                }
                for _ in range(0, 5)
            ),
            5,
        ),
    ],
)
async def test_genres_list_length(
    es_write_data,
    make_get_request,
    es_data: dict,
    expected_answer: int,
):
    await es_write_data("genres", es_data)

    status, response = await make_get_request("genres/")
    assert status == HTTPStatus.NOT_FOUND
    assert len(response) == expected_answer
