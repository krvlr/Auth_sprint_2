import random
import string
import uuid
from http import HTTPStatus

import pytest


async def test_persons_by_id_not_found(make_get_request):
    status, response = await make_get_request(f"persons/{0}")
    assert status == HTTPStatus.NOT_FOUND
    assert response == {"detail": "person not found"}


@pytest.mark.parametrize(
    "id, es_data, expected_answer",
    [
        (
            "ced104fa-d6b3-11ed-afa1-0242ac120002",
            (
                {
                    "id": "ced104fa-d6b3-11ed-afa1-0242ac120002",
                    "full_name": "Vasily Petrovich",
                    "films": [
                        {
                            "id": "6c162475-c7ed-4461-9184-001ef3d9f26e",
                            "roles": ["actor"],
                        },
                        {
                            "id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd",
                            "roles": ["actor"],
                        },
                    ],
                },
            ),
            {
                "id": "ced104fa-d6b3-11ed-afa1-0242ac120002",
                "full_name": "Vasily Petrovich",
                "films": [
                    {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "roles": ["actor"]},
                    {"id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "roles": ["actor"]},
                ],
            },
        ),
    ],
)
async def test_persons_by_id(
    es_write_data,
    make_get_request,
    id: str,
    es_data: dict,
    expected_answer: dict,
):
    await es_write_data("persons", es_data)

    status, response = await make_get_request(f"persons/{id}")
    assert status == HTTPStatus.OK
    assert response == expected_answer


async def test_persons_empty_list(make_get_request):
    status, response = await make_get_request("persons/")
    assert status == HTTPStatus.OK
    assert len(response) == 0


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "full_name": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                    "films": [
                        {
                            "id": "6c162475-c7ed-4461-9184-001ef3d9f26e",
                            "roles": ["actor"],
                        },
                        {
                            "id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd",
                            "roles": ["actor"],
                        },
                    ],
                }
                for _ in range(0, 10)
            ),
            10,
        ),
    ],
)
async def test_persons_cache(
    redis_client,
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("persons", es_data)
    await redis_client.flushall()
    keys = await redis_client.keys(pattern="*")

    assert len(keys) == 0

    status, response = await make_get_request("persons/", flush_cache=False)
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
            ({"id": str(i), "full_name": str(i), "films": []} for i in range(0, 10)),
            [
                {
                    "id": "4",
                    "full_name": "4",
                },
                {
                    "id": "5",
                    "full_name": "5",
                },
            ],
        ),
    ],
)
async def test_persons_pagination(
    es_write_data,
    make_get_request,
    page_number,
    page_size,
    es_data,
    expected_answer,
):
    await es_write_data("persons", es_data)

    status, response = await make_get_request(
        "persons/",
        params={"page_number": page_number, "page_size": page_size, "sort": "name"},
    )

    assert status == HTTPStatus.OK
    assert response == expected_answer


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": "c22ea5ae-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Cody",
                    "films": [],
                },
                {
                    "id": "bca615b8-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Honor",
                    "films": [],
                },
                {
                    "id": "6b8d0498-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Aon",
                    "films": [],
                },
            ),
            [
                {
                    "id": "6b8d0498-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Aon",
                },
                {
                    "id": "c22ea5ae-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Cody",
                },
                {
                    "id": "bca615b8-e027-11ed-b5ea-0242ac120002",
                    "full_name": "Honor",
                },
            ],
        ),
    ],
)
async def test_persons_sorting(
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("persons", es_data)

    status, response = await make_get_request("persons/", params={"sort": "full_name"})

    assert status == HTTPStatus.OK
    assert response == expected_answer


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "full_name": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                    "films": [],
                }
                for _ in range(0, 5)
            ),
            5,
        ),
    ],
)
async def test_persons_list_length(
    es_write_data,
    make_get_request,
    es_data: dict,
    expected_answer: int,
):
    await es_write_data("persons", es_data)

    status, response = await make_get_request("persons/")
    assert status == HTTPStatus.OK
    assert len(response) == expected_answer
