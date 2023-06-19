import logging
from functools import wraps
from http import HTTPStatus
from typing import Callable

from db.models.user import UserActionsHistory
from flask import request
from flask.json import loads
from flask_jwt_extended import current_user, decode_token
from werkzeug.http import parse_cookie

from db import alchemy

logger = logging.getLogger(__name__)


def get_user_id_from_response_jwt(response):
    return (
        decode_token(parse_cookie(response.headers["Set-Cookie"]).get("access_token_cookie"))
        .get("sub", {})
        .get("id")
    )


# FYI (delete) запись истории действий пользователя (в том числе входа) реализована здесь!!!
def log_action(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        request_device_info = request.user_agent.string

        response, status = func(*args, **kwargs)

        def save_user_action(user_id):
            alchemy.session.add(
                UserActionsHistory(
                    user_id=user_id,
                    action=func.__qualname__,
                    ip=request_ip,
                    device_info=request_device_info,
                )
            )
            alchemy.session.commit()

        if status == HTTPStatus.CREATED:
            user_data = loads(response.get_data()).get("data", {})
            save_user_action(user_data.get("id"))
        elif status == HTTPStatus.OK:
            if current_user:
                save_user_action(current_user.id)
            else:
                save_user_action(get_user_id_from_response_jwt(response))
        else:
            logger.info(
                f"Операция {func.__qualname__} со статусом {status} не сохранена "
                f"в истории действий пользователя. Ip: {request_ip}, "
                f"устройство: {request_device_info}"
            )

        return response, status

    return wrapper
