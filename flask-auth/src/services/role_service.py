from functools import lru_cache

from core.config import role_settings
from db.models.user import Role, User, UserActionsHistory, UserRole
from db.token_storage_adapter import TokenStatus, TokenStorageAdapter, get_redis_adapter
from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from models.auth_models import JwtPayload
from utils.exceptions import (
    AccountAddUserRoleException,
    AccountCheckUserRoleException,
    AccountCreateRoleException,
    AccountDeleteRoleException,
    AccountDeleteUserRoleException,
    AccountModifiedRoleException,
    AccountRoleDetailsException,
    AccountRolesDetailsException,
)

from db import alchemy


class RoleService:
    def __init__(self, token_storage_adapter: TokenStorageAdapter):
        self.token_storage = token_storage_adapter

    def create_role(self, name: str, description: str) -> dict:
        if Role.query.filter_by(name=name).first():
            raise AccountCreateRoleException(
                error_message="Подписка с таким названием уже существует."
            )

        role = Role(name=name, description=description)
        alchemy.session.add(role)
        alchemy.session.commit()

        return role.to_dict()

    def delete_role(self, name: str):
        role = Role.query.filter_by(name=name).first()

        if not role:
            raise AccountDeleteRoleException(
                error_message="Подписки с таким названием не существует."
            )

        alchemy.session.delete(role)
        alchemy.session.commit()

    def modified_role(self, name: str, new_name: str, new_description: str) -> dict:
        role = Role.query.filter_by(name=name).first()

        if not role:
            raise AccountModifiedRoleException(
                error_message="Подписки с таким названием не существует."
            )

        if Role.query.filter_by(name=new_name).first():
            raise AccountModifiedRoleException(
                error_message="Подписка с таким названием уже существует."
            )

        role.name = new_name
        role.description = new_description
        alchemy.session.commit()

        return role.to_dict()

    def role_details(self, name: str) -> dict:
        role = Role.query.filter_by(name=name).first()

        if not role:
            raise AccountRoleDetailsException(
                error_message="Подписки с таким названием не существует."
            )
        return role.to_dict()

    def roles_details(self) -> list:
        roles = Role.query.all()
        return [role.to_dict() for role in roles]

    def add_user_role(self, user_id: str, name: str):
        role = Role.query.filter_by(name=name).first()
        user = User.query.filter_by(id=user_id).first()

        if not role:
            raise AccountAddUserRoleException(
                error_message="Подписки с таким названием не существует."
            )

        if not user:
            raise AccountAddUserRoleException(
                error_message="Пользователя с таким идентификатором не существует."
            )

        if name in user.get_roles():
            raise AccountAddUserRoleException(
                error_message="У пользователя уже существует данная подписка."
            )

        role.users.append(user)
        alchemy.session.commit()

    def delete_user_role(self, user_id: str, name: str):
        role = Role.query.filter_by(name=name).first()
        user = User.query.filter_by(id=user_id).first()

        if not role:
            raise AccountDeleteUserRoleException(
                error_message="Подписки с таким названием не существует."
            )

        if not user:
            raise AccountDeleteUserRoleException(
                error_message="Пользователя с таким идентификатором не существует."
            )

        if name not in user.get_roles():
            raise AccountDeleteUserRoleException(
                error_message="У пользователя не существует данной подписки."
            )

        role.users.remove(user)
        alchemy.session.commit()

    def check_user_role(self, user_id: str, name: str):
        role = Role.query.filter_by(name=name).first()
        user = User.query.filter_by(id=user_id).first()

        if not role:
            raise AccountCheckUserRoleException(
                error_message="Подписки с таким названием не существует."
            )

        if not user:
            raise AccountCheckUserRoleException(
                error_message="Пользователя с таким идентификатором не существует."
            )

        if name not in user.get_roles():
            raise AccountCheckUserRoleException(
                error_message="У пользователя отсутствует данная подписка."
            )


@lru_cache()
def get_role_service(token_storage_adapter: TokenStorageAdapter = get_redis_adapter()):
    return RoleService(token_storage_adapter=token_storage_adapter)
