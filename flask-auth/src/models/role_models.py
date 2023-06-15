from pydantic import BaseModel, EmailStr, Field, validator


class CreateRoleRequest(BaseModel):
    name: str = Field(..., title="Название подписки")
    description: str = Field(..., title="Описание подписки")


class ModifiedRoleRequest(BaseModel):
    new_name: str = Field(..., title="Новое название подписки")
    new_description: str = Field(..., title="Новое описание подписки")


class AddUserRoleRequest(BaseModel):
    user_id: str = Field(..., title="Идентификатор пользователя")


class DeleteUserRoleRequest(BaseModel):
    user_id: str = Field(..., title="Идентификатор пользователя")


class CheckUserRoleRequest(BaseModel):
    user_id: str = Field(..., title="Идентификатор пользователя")


class RoleResponse(BaseModel):
    id: str = Field(..., title="Идентификатор роли")
    name: str = Field(..., title="Название подписки")
    description: str = Field(..., title="Описание подписки")


class PaginatorRequest(BaseModel):
    page_num: int = Field(default=1, title="Номер страницы", ge=1)
    page_size: int = Field(default=20, title="Размер страницы", ge=1, le=50)
