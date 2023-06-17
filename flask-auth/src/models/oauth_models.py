from abc import ABC

from pydantic import BaseModel, EmailStr, Field


class SocialUser(ABC, BaseModel):
    sub: str
    name: str
    email: EmailStr
    email_verified: bool


class GoogleUser(SocialUser):
    sub: str
    name: str
    email: EmailStr
    email_verified: bool


class YandexUser(SocialUser):
    sub: str = Field(alias="id")
    name: str = Field(alias="login")
    email: EmailStr = Field(alias="default_email")
    email_verified: bool = True
