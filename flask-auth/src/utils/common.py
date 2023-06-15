from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Type

from flask import abort, current_app, jsonify, request
from flask_jwt_extended import get_jwt
from pydantic import BaseModel, ValidationError


def get_data_from_body(request_model: Type[BaseModel]) -> Any:
    try:
        return request_model.parse_obj(request.get_json())
    except ValidationError as err:
        current_app.logger.error(f"{err.__class__.__name__}: {err}")
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, description=err.errors())


def get_data_from_params(request_model: Type[BaseModel]) -> Any:
    try:
        return request_model.parse_obj(request.args.to_dict())
    except ValidationError as err:
        current_app.logger.error(f"{err.__class__.__name__}: {err}")
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, description=err.errors())


def set_jwt_in_cookie(response: jsonify, access_token: str, refresh_token: str):
    response.set_cookie("access_token_cookie", value=access_token, httponly=True)
    response.set_cookie("refresh_token_cookie", value=refresh_token, httponly=True)


def check_is_admin(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt()["sub"]["is_admin"] == "False":
            abort(
                HTTPStatus.FORBIDDEN, description="Доступ запрещен, требуются права администратора!"
            )
        return func(*args, **kwargs)

    return wrapper
