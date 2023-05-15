import logging
import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="PROJECT_NAME")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    elastic_host: str = Field(default="127.0.0.1", env="ELASTIC_HOST")
    elastic_port: str = Field(default=9200, env="ELASTIC_PORT")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds: int = Field(default=60, env="CACHE_EXPIRE_SEC")
    debug_log_level: bool = Field(default=False, env="DEBUG")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    log_default_handlers = ["console"]

    class Config:
        env_file = ".env"


settings = Settings()

log_level = logging.DEBUG if settings.debug_log_level else logging.INFO
