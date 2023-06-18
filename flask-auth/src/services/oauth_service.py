import random
import string
from functools import lru_cache

from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti

from core.config import role_settings
from db import alchemy
from db.models.user import User, Role
from db.token_storage_adapter import TokenStorageAdapter, get_redis_adapter
from models.auth_models import JwtPayload
from models.oauth_models import SocialUser
from utils.exceptions import (
    AccountSigninException,
    AccountSignupException,
)


class OAuthService:
    def __init__(self, token_storage_adapter: TokenStorageAdapter):
        self.token_storage = token_storage_adapter

    @staticmethod
    def _create_random_password() -> str:
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for i in range(10))

    def _signin(self, user: User, device_info: str) -> dict:
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

    def _signup(
        self,
        name: str,
        email: str,
        social_id: str,
    ) -> User:
        if User.query.filter_by(email=email).first():
            raise AccountSignupException(
                error_message="Пользователь с такой почтой уже существует."
            )

        role = Role.query.filter_by(name=role_settings.default_user_role).first()
        user = User(
            login=name + social_id,
            email=email,
            password=self._create_random_password(),
            is_admin=False,
            is_verified=True,
        )

        alchemy.session.add(user)
        role.users.append(user)
        alchemy.session.commit()

        return user

    def signin_social_user(self, user: SocialUser) -> dict:
        if not user.email_verified:
            raise AccountSigninException(error_message="Пользователь не подтвердил учетную запись")

        user_db = User.query.filter_by(email=user.email).one_or_none()

        if not user_db:
            user_db = self._signup(name=user.name, email=user.email, social_id=user.sub)

        return self._signin(user_db, device_info=request.user_agent.string)


@lru_cache
def get_oauth_service(token_storage_adapter: TokenStorageAdapter = get_redis_adapter()):
    return OAuthService(token_storage_adapter=token_storage_adapter)
