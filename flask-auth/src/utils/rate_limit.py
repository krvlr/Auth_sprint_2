import datetime
from functools import wraps
from http import HTTPStatus

from core.config import common_settings, redis_settings
from flask import jsonify
from flask_jwt_extended import get_jwt
from models.common import BaseResponse
from redis import Redis

redis_rate_limit_conn = Redis(
    host=redis_settings.host,
    port=redis_settings.port,
    db=9,
)


def limit_leaky_bucket(func):
    @wraps(func)
    def wrapper():
        jti = get_jwt()

        pipe = redis_rate_limit_conn.pipeline()
        now = datetime.datetime.now()
        key = f'{jti["sub"]["id"]}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = pipe.execute()

        request_number = result[0]
        if request_number > common_settings.request_limit_per_minute:
            return (
                jsonify(BaseResponse(success=False, error="Слишком много запросов").dict()),
                HTTPStatus.TOO_MANY_REQUESTS,
            )

        return func()

    return wrapper
