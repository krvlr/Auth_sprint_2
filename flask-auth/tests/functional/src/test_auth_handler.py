from collections import defaultdict
from http import HTTPStatus

import pytest
from utils.helpers import get_cookies


@pytest.mark.parametrize(
    "cases",
    [
        [
            {
                "endpoint": "signup",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.CREATED, "success": True},
            },
            {
                "endpoint": "signup",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.BAD_REQUEST, "success": False},
            },
        ],
        [
            {
                "endpoint": "signup",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.CREATED, "success": True},
            },
            {
                "endpoint": "signup",
                "request": {
                    "login": "kvlr",
                    "email": "kvlr@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.CREATED, "success": True},
            },
        ],
        [
            {
                "endpoint": "signup",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.CREATED, "success": True},
            }
        ],
    ],
)
async def test_signup(make_post_request, postgre_engine, cases: list):
    for case in cases:
        response = await make_post_request(endpoint=case["endpoint"], data=case["request"])
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        [
            {
                "endpoint": "signup",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.CREATED, "success": True},
            },
            {
                "endpoint": "signin",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.OK, "success": True},
            },
        ],
        [
            {
                "endpoint": "signin",
                "request": {
                    "login": "kira",
                    "email": "kira@me.com",
                    "password": "12345678",
                },
                "response": {"status": HTTPStatus.UNAUTHORIZED, "success": False},
            },
        ],
    ],
)
async def test_signin(make_post_request, postgre_engine, cases: list):
    for case in cases:
        response = await make_post_request(endpoint=case["endpoint"], data=case["request"])
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        {
            "signup": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
                {
                    "request": {
                        "login": "kvlr",
                        "email": "kvlr@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
            ],
            "signin": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
                {
                    "request": {
                        "login": "kvlr",
                        "email": "kvlr@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
            ],
            "refresh": [
                {"login": "kira", "response": {"status": HTTPStatus.OK, "success": True}},
                {"login": "kvlr", "response": {"status": HTTPStatus.OK, "success": True}},
            ],
        },
    ],
)
async def test_refresh(make_post_request, make_get_request, postgre_engine, cases: list):
    for case in cases["signup"]:
        response = await make_post_request(
            endpoint="signup", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    user_cookies = {}

    for case in cases["signin"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        user_cookies[case["request"]["login"]] = get_cookies(
            simple_cookies=response.cookies, filters=["refresh_token_cookie"]
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["refresh"]:
        refresh_token_cookie = user_cookies[case["login"]]["refresh_token_cookie"]
        response = await make_post_request(
            endpoint="refresh", token=refresh_token_cookie, flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        {
            "signup": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
                {
                    "request": {
                        "login": "kvlr",
                        "email": "kvlr@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
            ],
            "signin": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
                {
                    "request": {
                        "login": "kvlr",
                        "email": "kvlr@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
            ],
            "signout": [
                {"login": "kira", "response": {"status": HTTPStatus.OK, "success": True}},
                {"login": "kvlr", "response": {"status": HTTPStatus.OK, "success": True}},
            ],
            "refresh": [
                {"login": "kira", "response": {"status": HTTPStatus.BAD_REQUEST, "success": False}},
                {"login": "kvlr", "response": {"status": HTTPStatus.BAD_REQUEST, "success": False}},
            ],
        },
    ],
)
async def test_signout(make_post_request, make_get_request, postgre_engine, cases: list):
    for case in cases["signup"]:
        response = await make_post_request(
            endpoint="signup", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    user_cookies = {}

    for case in cases["signin"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        user_cookies[case["request"]["login"]] = get_cookies(
            simple_cookies=response.cookies, filters=["access_token_cookie", "refresh_token_cookie"]
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["signout"]:
        access_token_cookie = user_cookies[case["login"]]["access_token_cookie"]
        refresh_token_cookie = user_cookies[case["login"]]["refresh_token_cookie"]
        data = {"refresh_token": refresh_token_cookie}
        response = await make_post_request(
            endpoint="signout", data=data, token=access_token_cookie, flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["refresh"]:
        refresh_token_cookie = user_cookies[case["login"]]["refresh_token_cookie"]
        response = await make_post_request(
            endpoint="refresh", token=refresh_token_cookie, flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        {
            "signup": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
            ],
            "signin": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
            ],
            "signout/all": [
                {"login": "kira", "response": {"status": HTTPStatus.OK, "success": True}},
            ],
            "refresh": [
                {"login": "kira", "response": {"status": HTTPStatus.BAD_REQUEST, "success": False}},
            ],
        },
    ],
)
async def test_signout_all(make_post_request, make_get_request, postgre_engine, cases: list):
    for case in cases["signup"]:
        response = await make_post_request(
            endpoint="signup", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    user_cookies = defaultdict(list)

    for case in cases["signin"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        user_cookies[case["request"]["login"]].append(
            get_cookies(
                simple_cookies=response.cookies,
                filters=["access_token_cookie", "refresh_token_cookie"],
            )
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["signout/all"]:
        access_token_cookie = user_cookies[case["login"]][0]["access_token_cookie"]
        response = await make_post_request(
            endpoint="signout/all", token=access_token_cookie, flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["refresh"]:
        for cookies in user_cookies[case["login"]]:
            refresh_token_cookie = cookies["refresh_token_cookie"]
            response = await make_post_request(
                endpoint="refresh", token=refresh_token_cookie, flush_cache=False
            )
            assert response.status == case["response"]["status"]
            assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        {
            "signup": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
            ],
            "signin": {
                "befor_change_password": [
                    {
                        "request": {
                            "login": "kira",
                            "email": "kira@me.com",
                            "password": "12345678",
                        },
                        "response": {"status": HTTPStatus.OK, "success": True},
                    },
                ],
                "after_change_password": [
                    {
                        "request": {
                            "login": "kira",
                            "email": "kira@me.com",
                            "password": "boris_britva",
                        },
                        "response": {"status": HTTPStatus.OK, "success": True},
                    },
                    {
                        "request": {
                            "login": "kira",
                            "email": "kira@me.com",
                            "password": "12345678",
                        },
                        "response": {"status": HTTPStatus.UNAUTHORIZED, "success": False},
                    },
                ],
            },
            "password/change": [
                {
                    "login": "kira",
                    "request": {
                        "old_password": "12345678",
                        "new_password": "boris_britva",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
            ],
        },
    ],
)
async def test_password_change(make_post_request, postgre_engine, cases: list):
    for case in cases["signup"]:
        response = await make_post_request(
            endpoint="signup", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    user_cookies = {}

    for case in cases["signin"]["befor_change_password"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        user_cookies[case["request"]["login"]] = get_cookies(
            simple_cookies=response.cookies,
            filters=["access_token_cookie"],
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["password/change"]:
        access_token_cookie = user_cookies[case["login"]]["access_token_cookie"]
        response = await make_post_request(
            endpoint="password/change",
            data=case["request"],
            token=access_token_cookie,
            flush_cache=False,
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["signin"]["after_change_password"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]


@pytest.mark.parametrize(
    "cases",
    [
        {
            "signup": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.CREATED, "success": True},
                },
            ],
            "signin": [
                {
                    "request": {
                        "login": "kira",
                        "email": "kira@me.com",
                        "password": "12345678",
                    },
                    "response": {"status": HTTPStatus.OK, "success": True},
                },
            ],
            "history": [
                {"login": "kira", "response": {"status": HTTPStatus.OK, "success": True}},
            ],
        },
    ],
)
async def test_history(make_post_request, make_get_request, postgre_engine, cases: list):
    for case in cases["signup"]:
        response = await make_post_request(
            endpoint="signup", data=case["request"], flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    user_cookies = {}

    for case in cases["signin"]:
        response = await make_post_request(
            endpoint="signin", data=case["request"], flush_cache=False
        )
        user_cookies[case["request"]["login"]] = get_cookies(
            simple_cookies=response.cookies,
            filters=["access_token_cookie"],
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]

    for case in cases["history"]:
        access_token_cookie = user_cookies[case["login"]]["access_token_cookie"]
        response = await make_get_request(
            endpoint="history", token=access_token_cookie, flush_cache=False
        )
        assert response.status == case["response"]["status"]
        assert response.body.get("success") == case["response"]["success"]
