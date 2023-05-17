import random
import string
import uuid
from http import HTTPStatus

import pytest


async def test_film_by_id_not_found(make_get_request):
    status, response = await make_get_request(f"films/{0}")
    assert status == HTTPStatus.NOT_FOUND
    assert response == {"detail": "film not found"}


@pytest.mark.parametrize(
    "id, es_data, expected_answer",
    [
        (
            "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
            (
                {
                    "id": "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
                    "title": "Star Wars: Clone Wars",
                    "imdb_rating": 7.8,
                    "description": "...",
                    "actors": [
                        {
                            "id": "6dd77305-18ee-4d2e-9215-fd1a496ccfdf",
                            "name": "Mat Lucas",
                        },
                        {
                            "id": "8746ff78-577b-4bef-a7f7-1db05a102def",
                            "name": "James Arnold Taylor",
                        },
                        {
                            "id": "96185bee-1b14-4320-84ff-def00c07593c",
                            "name": "André Sogliuzzo",
                        },
                        {
                            "id": "b4e1b2bd-7f36-4322-8a96-0baecf121424",
                            "name": "Grey Griffin",
                        },
                    ],
                    "writers": [],
                    "directors": [],
                    "genres": [
                        {
                            "id": "120a21cf-9097-479e-904a-13dd7198c1dd",
                            "name": "Adventure",
                        },
                        {
                            "id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                            "name": "Action",
                        },
                        {
                            "id": "6c162475-c7ed-4461-9184-001ef3d9f26e",
                            "name": "Sci-Fi",
                        },
                        {
                            "id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd",
                            "name": "Fantasy",
                        },
                    ],
                },
            ),
            {
                "id": "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
                "title": "Star Wars: Clone Wars",
                "imdb_rating": 7.8,
                "description": "...",
                "actors": [
                    {"id": "6dd77305-18ee-4d2e-9215-fd1a496ccfdf", "name": "Mat Lucas"},
                    {
                        "id": "8746ff78-577b-4bef-a7f7-1db05a102def",
                        "name": "James Arnold Taylor",
                    },
                    {
                        "id": "96185bee-1b14-4320-84ff-def00c07593c",
                        "name": "André Sogliuzzo",
                    },
                    {
                        "id": "b4e1b2bd-7f36-4322-8a96-0baecf121424",
                        "name": "Grey Griffin",
                    },
                ],
                "writers": [],
                "directors": [],
                "genres": [
                    {"id": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
                    {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
                    {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"},
                    {"id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "name": "Fantasy"},
                ],
            },
        ),
    ],
)
async def test_film_by_id(
    es_write_data,
    make_get_request,
    id: str,
    es_data: dict,
    expected_answer: dict,
):
    await es_write_data("movies", es_data)

    status, response = await make_get_request(f"films/{id}")
    assert status == HTTPStatus.OK
    assert response == expected_answer


async def test_film_empty_list(make_get_request):
    status, response = await make_get_request("films/")
    assert status == HTTPStatus.OK
    assert len(response) == 0


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "title": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                    "imdb_rating": random.randint(0, 10),
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                }
                for _ in range(0, 10)
            ),
            10,
        ),
    ],
)
async def test_film_list_cache(
    redis_client,
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("movies", es_data)
    await redis_client.flushall()
    keys = await redis_client.keys(pattern="*")

    assert len(keys) == 0

    status, response = await make_get_request("films/", flush_cache=False)
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
                    "title": str(i),
                    "imdb_rating": i,
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                }
                for i in range(0, 10)
            ),
            [
                {
                    "id": "4",
                    "title": "4",
                    "imdb_rating": 4.0,
                },
                {
                    "id": "5",
                    "title": "5",
                    "imdb_rating": 5.0,
                },
            ],
        ),
    ],
)
async def test_film_pagination(
    es_write_data,
    make_get_request,
    page_number,
    page_size,
    es_data,
    expected_answer,
):
    await es_write_data("movies", es_data)

    status, response = await make_get_request(
        "films/",
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
                    "id": "fe758dd4-9063-42d4-bf08-bdc7dbae3479",
                    "title": "Star Trek: Tactical Assault",
                    "imdb_rating": 7.2,
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                },
                {
                    "id": "fe4acdc6-4b23-4437-92fb-b73872b5dca2",
                    "title": "Star Trek: D·A·C",
                    "imdb_rating": 6.7,
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                },
                {
                    "id": "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
                    "title": "Star Wars: Clone Wars",
                    "imdb_rating": 7.8,
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                },
            ),
            [
                {
                    "id": "fdfc8266-5ece-4d85-b614-3cfe9be97b71",
                    "title": "Star Wars: Clone Wars",
                    "imdb_rating": 7.8,
                },
                {
                    "id": "fe758dd4-9063-42d4-bf08-bdc7dbae3479",
                    "title": "Star Trek: Tactical Assault",
                    "imdb_rating": 7.2,
                },
                {
                    "id": "fe4acdc6-4b23-4437-92fb-b73872b5dca2",
                    "title": "Star Trek: D·A·C",
                    "imdb_rating": 6.7,
                },
            ],
        ),
    ],
)
async def test_film_sorting(
    es_write_data,
    make_get_request,
    es_data,
    expected_answer,
):
    await es_write_data("movies", es_data)

    status, response = await make_get_request("films/", params={"sort": "-imdb_rating"})

    assert status == HTTPStatus.OK
    assert response == expected_answer


@pytest.mark.parametrize(
    "es_data, expected_answer",
    [
        (
            (
                {
                    "id": str(uuid.uuid4()),
                    "title": "".join(random.choice(string.ascii_lowercase) for _ in range(10)),
                    "imdb_rating": random.randint(0, 10),
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                }
                for _ in range(0, 5)
            ),
            5,
        ),
    ],
)
async def test_films_list_length(
    es_write_data,
    make_get_request,
    es_data: dict,
    expected_answer: int,
):
    await es_write_data("movies", es_data)

    status, response = await make_get_request("films/")
    assert status == HTTPStatus.OK
    assert len(response) == expected_answer
