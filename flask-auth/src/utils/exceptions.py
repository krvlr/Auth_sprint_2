import traceback
from http import HTTPStatus

from flask import jsonify
from models.common import BaseResponse
from werkzeug.exceptions import (
    Forbidden,
    MethodNotAllowed,
    UnprocessableEntity,
    UnsupportedMediaType,
)


def add_base_exceptions_handlers(app):
    @app.errorhandler(UnprocessableEntity)
    def unprocessable_entity_exception(ex: UnprocessableEntity):
        app.logger.error(msg=ex.description)
        return (
            jsonify(BaseResponse(success=False, error="Ошибка формата входных данных.").dict()),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    @app.errorhandler(UnsupportedMediaType)
    def unsupported_media_type(ex: UnsupportedMediaType):
        app.logger.error(msg=ex.description)
        return (
            jsonify(BaseResponse(success=False, error="Ошибка состава запроса.").dict()),
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        )

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(ex: MethodNotAllowed):
        app.logger.error(msg=ex.description)
        return (
            jsonify(
                BaseResponse(success=False, error="Метод не разрешен для запрошенного URL.").dict()
            ),
            HTTPStatus.METHOD_NOT_ALLOWED,
        )

    @app.errorhandler(Forbidden)
    def forbidden(ex: Forbidden):
        app.logger.error(msg=ex.description)
        return (
            jsonify(
                BaseResponse(
                    success=False, error="Доступ запрещен, требуются админские права!"
                ).dict()
            ),
            HTTPStatus.FORBIDDEN,
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


class AccountCreateRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке создания подписки. {error_message}"


class AccountRoleDetailsException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке получения информации о подписке. {error_message}"


class AccountRolesDetailsException(Exception):
    def __init__(self, error_message: str):
        self.error_message = (
            f"Ошибка при попытке получения информации о всех доступных подписках. {error_message}"
        )


class AccountDeleteRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке удаления подписки. {error_message}"


class AccountModifiedRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке изменения подписки. {error_message}"


class AccountAddUserRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке выдачи пользователю подписки. {error_message}"


class AccountDeleteUserRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = f"Ошибка при попытке удаления подписки у пользователя. {error_message}"


class AccountCheckUserRoleException(Exception):
    def __init__(self, error_message: str):
        self.error_message = (
            f"Ошибка при попытке проверки наличия подписки у пользователя. {error_message}"
        )
