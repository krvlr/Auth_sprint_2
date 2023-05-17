from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    elastic_host: str = Field(default="elasticsearch", env="ELASTIC_HOST")
    elastic_port: str = Field(default=9200, env="ELASTIC_PORT")
    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    api_url: str = Field(default="http://api:8000/api/v1", evn="API_URL")

    class Config:
        env_file = ".env"


test_settings = TestSettings()
