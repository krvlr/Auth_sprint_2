from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    "es_index, endpoint, query_data, es_data, expected_answer",
    [
        (
            "movies",
            "films/search",
            {"query": "title=Star Wars", "sort": "id"},
            (
                {
                    "id": str(_),
                    "title": "Star Wars: Clone Wars" if not _ % 2 else "Cars!",
                    "imdb_rating": 7.8,
                    "description": "...",
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                }
                for _ in range(60)
            ),
            {
                "status": HTTPStatus.OK,
                "response": [
                    {
                        "id": str(_),
                        "title": "Star Wars: Clone Wars",
                        "imdb_rating": 7.8,
                    }
                    for _ in range(0, 40, 2)
                ],
            },
        ),
        (
            "movies",
            "films/search",
            {"query": "title=brat pokemon", "sort": "id"},
            (
                {
                    "id": str(_),
                    "title": "Star Wars: Clone Wars" if not _ % 2 else "Cars!",
                    "imdb_rating": 7.8,
                    "description": "...",
                    "actors": [],
                    "writers": [],
                    "directors": [],
                    "genres": [],
                }
                for _ in range(60)
            ),
            {"status": HTTPStatus.OK, "response": []},
        ),
        (
            "persons",
            "persons/search",
            {"query": "full_name=Vasily", "sort": "id"},
            (
                {
                    "id": str(_),
                    "full_name": "Vasily Petrovich" if not _ % 2 else "Pedrila Petrovitch",
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
                for _ in range(60)
            ),
            {
                "status": HTTPStatus.OK,
                "response": [
                    {
                        "id": str(_),
                        "full_name": "Vasily Petrovich" if not _ % 2 else "Pedrila Petrovitch",
                    }
                    for _ in range(0, 40, 2)
                ],
            },
        ),
        (
            "persons",
            "persons/search",
            {"query": "full_name=hutch", "sort": "id"},
            (
                {
                    "id": str(_),
                    "full_name": "Vasily Petrovich" if not _ % 2 else "Pedrila Petrovitch",
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
                for _ in range(60)
            ),
            {"status": HTTPStatus.OK, "response": []},
        ),
    ],
)
async def test_search(
    es_write_data,
    make_get_request,
    es_index,
    endpoint,
    query_data,
    es_data,
    expected_answer,
):
    await es_write_data(es_index, es_data)

    status, response = await make_get_request(endpoint, params=query_data)

    assert status == expected_answer["status"]
    assert response == expected_answer["response"]
