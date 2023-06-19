from functools import lru_cache

from core.config import role_settings
from db.models.user import Role, User, UserActionsHistory
from db.token_storage_adapter import TokenStatus, TokenStorageAdapter, get_redis_adapter
from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from models.auth_models import JwtPayload
from utils.exceptions import (
    AccountHistoryException,
    AccountPasswordChangeException,
    AccountRefreshException,
    AccountSigninException,
    AccountSignoutAllException,
    AccountSignoutException,
    AccountSignupException,
)

from db import alchemy


class AuthService:
    def __init__(self, token_storage_adapter: TokenStorageAdapter):
        self.token_storage = token_storage_adapter

    def create_jwt_tokens(self, user: User, device_info: str) -> dict:
        identity = dict(
            JwtPayload(
                id=str(user.id),
                device_info=device_info,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_admin=user.is_admin,
                roles=user.get_roles(),
            )
        )

        access_token = create_access_token(identity=identity)
        self.token_storage.create(
            user_id=str(user.id),
            jti=get_jti(access_token),
            delta_expire=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        )

        refresh_token = create_refresh_token(identity=identity)
        self.token_storage.create(
            user_id=str(user.id),
            jti=get_jti(refresh_token),
            delta_expire=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
        )
        return dict(access_token=access_token, refresh_token=refresh_token)

    def signup(
        self,
        login: str,
        email: str,
        password: str,
    ) -> dict:
        if User.query.filter_by(login=login).first():
            raise AccountSignupException(
                error_message="Пользователь с таким логином уже существует."
            )

        if User.query.filter_by(email=email).first():
            raise AccountSignupException(
                error_message="Пользователь с такой почтой уже существует."
            )

        role = Role.query.filter_by(name=role_settings.default_user_role).first()
        user = User(login=login, email=email, password=password, is_admin=False)

        alchemy.session.add(user)
        role.users.append(user)
        alchemy.session.commit()

        return user.to_dict()

    def signin(
        self,
        login: str,
        password: str,
    ) -> dict:
        user = User.query.filter_by(login=login).one_or_none()

        if user and user.verify_password(password):
            return self.create_jwt_tokens(
                user=user,
                device_info=request.user_agent.string,
            )

        raise AccountSigninException(error_message="Неверный логин или пароль.")

    def refresh(self, user: User, device_info: str, refresh_jti: str) -> dict:
        status = self.token_storage.get_status(user_id=str(user.id), jti=refresh_jti)

        if status == TokenStatus.NOT_FOUND:
            raise AccountRefreshException(error_message="Истек срок действия refresh токена.")
        elif status == TokenStatus.BLOCKED:
            raise AccountRefreshException(error_message="Данный refresh токен более не валиден.")

        self.token_storage.block(user_id=str(user.id), jti=refresh_jti)

        return self.create_jwt_tokens(user=user, device_info=device_info)

    def password_change(
        self,
        user: User,
        access_jti: str,
        old_password: str,
        new_password: str,
    ):
        status = self.token_storage.get_status(user_id=str(user.id), jti=access_jti)
        if status == TokenStatus.NOT_FOUND:
            raise AccountPasswordChangeException(error_message="Истек срок действия access токена.")
        elif status == TokenStatus.BLOCKED:
            raise AccountPasswordChangeException(
                error_message="Данный access токен более не валиден."
            )

        if not user.verify_password(old_password):
            raise AccountPasswordChangeException(error_message="Старый пароль введен неверно.")

        user.password = new_password
        alchemy.session.commit()

    def signout(self, user_id: str, refresh_jti: str, access_jti: str):
        access_status = self.token_storage.get_status(user_id=user_id, jti=access_jti)

        if access_status == TokenStatus.NOT_FOUND:
            raise AccountSignoutException(error_message="Истек срок действия access токена.")
        elif access_status == TokenStatus.BLOCKED:
            raise AccountSignoutException(error_message="Данный access токен более не валиден.")

        self.token_storage.block(user_id=user_id, jti=access_jti)
        self.token_storage.block(user_id=user_id, jti=refresh_jti)

    def signout_all(
        self,
        user_id: str,
        access_jti: str,
    ):
        status = self.token_storage.get_status(user_id=user_id, jti=access_jti)

        if status == TokenStatus.NOT_FOUND:
            raise AccountSignoutAllException(error_message="Истек срок действия access токена.")
        elif status == TokenStatus.BLOCKED:
            raise AccountSignoutAllException(error_message="Данный access токен более не валиден.")

        self.token_storage.block_for_pattern(pattern=f"{user_id}:*")

    def history(
        self,
        user_id: str,
        access_jti: str,
        page_num: int,
        page_size: int,
    ) -> dict:
        status = self.token_storage.get_status(user_id=user_id, jti=access_jti)

        if status == TokenStatus.NOT_FOUND:
            raise AccountHistoryException(error_message="Истек срок действия access токена.")
        elif status == TokenStatus.BLOCKED:
            raise AccountHistoryException(error_message="Данный access токен более не валиден.")

        history = (
            UserActionsHistory.query.filter_by(user_id=user_id)
            .order_by(UserActionsHistory.created.desc())
            .paginate(
                page=page_num,
                per_page=page_size,
                count=True,
            )
        )

        return {
            "total_results": history.total,
            "history": [r.to_dict() for r in history],
        }


@lru_cache
def get_auth_service(token_storage_adapter: TokenStorageAdapter = get_redis_adapter()):
    return AuthService(token_storage_adapter=token_storage_adapter)
