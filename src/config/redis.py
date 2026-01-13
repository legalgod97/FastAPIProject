from redis.asyncio import Redis
from src.config.config import Settings

settings = Settings()

redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)

CACHE_TTL = settings.cache_ttl