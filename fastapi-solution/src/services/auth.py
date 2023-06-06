import logging
from http import HTTPStatus

import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError
from pydantic import BaseModel, Field, ValidationError

from core.config import settings

logger = logging.getLogger(__name__)


class SubRequiredFields(BaseModel):
    is_active: bool = Field(..., title="Активный пользователь")
    is_admin: bool = Field(..., title="Администратор")
    is_premium: bool = Field(..., title="Премиум пользователь")


class JWTBearerPremium(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный код")

        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Ошибка схемы")

        try:
            decoded_token = jwt.decode(
                credentials.credentials,
                settings.secret_key,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError as ex:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Истек срок действия JWT access токена"
            )
        except Exception as ex:
            logger.exception("Ошибка проверки JWT токена")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный JWT токен")

        if not decoded_token.get("type") == "access":
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Тип токена не access")

        if not self.is_authorized_account(decoded_token):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Нет прав доступа")

        return credentials.credentials

    @staticmethod
    def is_authorized_account(decoded_token: dict) -> bool:
        try:
            sub = SubRequiredFields(**decoded_token.get("sub", {}))
            return sub.is_active and (sub.is_admin or sub.is_premium)
        except ValidationError:
            logger.exception("Ошибка чтения payload JWT токена")
            return False
