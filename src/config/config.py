from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from config.kafka import KafkaSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    cache_ttl: int = 60 * 60

    kafka: KafkaSettings = KafkaSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"