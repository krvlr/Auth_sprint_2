from pathlib import Path

from pydantic import BaseSettings, Field, AnyUrl

BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATION_DIR = BASE_DIR / "db" / "migrations"


class BaseConfig(BaseSettings):
    class Config:
        env_file = ".env"


class LoggerSettings(BaseConfig):
    level: str = Field(default="INFO", env="LOGGING_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    default_handlers: list = ["console"]


class CommonSettings(BaseConfig):
    secret_key: str = Field(repr=False, env="FLASK_SECRET_KEY")
    debug: bool = Field(default=True, env="DEBUG")
    host: str = Field(default="0.0.0.0")
    port: str = Field(default="8000")
    request_limit_per_minute: int = Field(default=20, env="REQUEST_LIMIT_PER_MINUTE")


class PostgreSettings(BaseConfig):
    host: str = Field(default="127.0.0.1", env="AUTH_DB_HOST")
    port: str = Field(default="5432", env="AUTH_DB_PORT")
    name: str = Field(default="auth_database", env="AUTH_DB_NAME")
    user: str = Field(default="admin", env="AUTH_DB_USER")
    password: str = Field(default="admin", env="AUTH_DB_PASSWORD")

    def get_db_uri(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseConfig):
    host: str = Field(default="127.0.0.1", env="AUTH_REDIS_HOST")
    port: str = Field(default="6379", env="AUTH_REDIS_PORT")


class JWTSettings(BaseConfig):
    cookie_secure: str = Field(default="False", repr=False, env="JWT_COOKIE_SECURE")
    token_location: str = Field(default="cookies", repr=False, env="JWT_TOKEN_LOCATION")
    secret_key: str = Field(default="SUPER-SECRET-KEY", repr=False, env="JWT_SECRET_KEY")
    access_token_expires: int = Field(default=1, env="JWT_ACCESS_TOKEN_EXPIRES")
    refresh_token_expires: int = Field(default=30, env="JWT_REFRESH_TOKEN_EXPIRES")


class RoleSettings(BaseConfig):
    default_user_role: str = Field(default="default", env="DEFAULT_USER_ROLE")
    initial_user_roles: str = Field(default="default", env="INITIAL_USER_ROLES")
    initial_user_descrition_roles: str = Field(
        default="Base rights for a registered user", env="INITIAL_USER_DESCRIPTION_ROLES"
    )

    def get_initial_roles(self):
        for role, descrition in zip(
            self.initial_user_roles.split(", "), self.initial_user_descrition_roles.split(", ")
        ):
            yield role, descrition


class JaegerSettings(BaseConfig):
    enable_tracer: bool = Field(default=True, env="ENABLE_TRACER")
    host: str = Field(default="127.0.0.1", env="JAEGER_HOST")
    port: int = Field(default=6831, env="JAEGER_PORT")


class OAuthGoogleSettings(BaseConfig):
    client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    client_secret: str = Field(default="", env="GOOGLE_CLIENT_SECRET", repr=False)
    conf_url: AnyUrl = Field(
        default="https://accounts.google.com/.well-known/openid-configuration",
        env="GOOGLE_CONF_URL",
    )
    scope: str = Field(default="openid email profile", env="")


class OAuthYandexSettings(BaseConfig):
    client_id: str = Field(default="", env="YANDEX_CLIENT_ID")
    client_secret: str = Field(default="", env="YANDEX_CLIENT_SECRET", repr=False)
    access_token_url: AnyUrl = Field(
        default="https://oauth.yandex.ru/token",
        env="YANDEX_ACCESS_TOKEN_URL",
    )
    authorize_url: AnyUrl = Field(
        default="https://oauth.yandex.ru/authorize",
        env="YANDEX_AUTHORIZE_URL",
    )
    user_info_url: AnyUrl = Field(
        default="https://login.yandex.ru/info",
        env="YANDEX_USER_INFO_URL",
    )


logger_settings = LoggerSettings()
common_settings = CommonSettings()
postgre_settings = PostgreSettings()
redis_settings = RedisSettings()
jwt_settings = JWTSettings()
role_settings = RoleSettings()
jaeger_settings = JaegerSettings()
oauth_google_settings = OAuthGoogleSettings()
oauth_yandex_settings = OAuthYandexSettings()
