from pydantic import BaseModel, EmailStr, Field, validator
from utils.exceptions import AccountPasswordChangeException, AccountSignupException


class SignupRequest(BaseModel):
    login: str = Field(..., title="Логин")
    email: EmailStr = Field(..., title="Почта")
    password: str = Field(..., title="Пароль")

    @validator("login")
    def login_alphanumeric(cls, v):
        if not v.isalnum():
            raise AccountSignupException(
                error_message="Логин может содержать только числа и буквенные символы."
            )
        return v

    @validator("password")
    def password_length(cls, v):
        if not (6 <= len(v) <= 72):
            raise AccountSignupException(
                error_message="Пароль не удовлетворяет требованиям безопасности. "
                "Длина пароля должна содержать не менее 6 и не более 72 символов."
            )
        return v


class AuthResponse(BaseModel):
    refresh_token: str = Field(..., title="Refresh токен")
    access_token: str = Field(..., title="Access токен")


class SigninRequest(BaseModel):
    login: str = Field(..., title="Логин")
    password: str = Field(..., title="Пароль")


class SignoutRequest(BaseModel):
    refresh_token: str = Field(..., title="Refresh токен")


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., title="Старый пароль")
    new_password: str = Field(..., title="Новый пароль")

    @validator("new_password")
    def password_length(cls, v):
        if not (6 <= len(v) <= 72):
            raise AccountPasswordChangeException(
                error_message="Пароль не удовлетворяет требованиям безопасности. "
                "Длина пароля должна содержать не менее 6 и не более 72 символов."
            )
        return v


class PaginatorRequest(BaseModel):
    page_num: int = Field(default=1, title="Номер страницы", ge=1)
    page_size: int = Field(default=20, title="Размер страницы", ge=1, le=50)


class JwtPayload(BaseModel):
    id: str = Field(..., title="Идентификатор пользователя")
    device_info: str = Field(..., title="Информация о устройстве")
    is_active: str = Field(..., title="Признак активного пользователя")
    is_verified: str = Field(..., title="Признак верифицированного пользователя")
    is_admin: str = Field(..., title="Признак администратора")
    roles: list = Field(..., title="Список ролей пользователя")
