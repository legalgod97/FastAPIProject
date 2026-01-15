from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = Field(
        default="kafka:9092",
    )

    users_created_topic: str = Field(
        default="users.created",
    )

    class Config:
        env_prefix = "KAFKA_"