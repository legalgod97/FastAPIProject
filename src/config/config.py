import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    postgres_url: str = Field(env="PostgresDsn")

    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")

    cache_ttl: int = Field(default=60 * 60, env="CACHE_TTL")

    class Config:
        env_file = ".env"