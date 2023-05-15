import traceback
from http import HTTPStatus

from flask import jsonify
from werkzeug.exceptions import UnprocessableEntity, UnsupportedMediaType

from models.common import BaseResponse


def add_base_exceptions_handlers(app):
    @app.errorhandler(UnprocessableEntity)
    def unprocessable_entity_exception(ex: UnprocessableEntity):
        app.logger.error(msg=ex.description)
        return (
            jsonify(BaseResponse(success=False, error="Ошибка формата входных данных.").dict()),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(UnsupportedMediaType)
    def unprocessable_media_type(ex: UnsupportedMediaType):
        app.logger.error(msg=ex.description)
        return (
            jsonify(BaseResponse(success=False, error="Ошибка состава запроса.").dict()),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(Exception)
    def handle_exception(ex):
        app.logger.error(msg=traceback.format_exc())
        return (
            jsonify(BaseResponse(success=False, error="Неизвестная ошибка.").dict()),
            HTTPStatus.BAD_REQUEST,
        )


class AccountSignupException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка регистрации пользователя. {error_message}"


class AccountSigninException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка аутентификации пользователя. {error_message}"


class AccountRefreshException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке воспользоваться refresh токеном. {error_message}"


class AccountPasswordChangeException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка изменения пароля пользователя. {error_message}"


class AccountSignoutException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке выйти из аккаунта. {error_message}"


class AccountSignoutAllException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке выйти со всех устройств аккаунта. {error_message}"


class AccountHistoryException(Exception):
    def __init__(self, error_message: str):
        self.error_message = (
            f"Ошибка при попытке получения истории действий пользователя. {error_message}"
        )
