from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.config.redis import redis, CACHE_TTL
from src.messaging.kafka.producer import KafkaProducer
from src.services.events.users import UserCreatedEvent, UserUpdatedEvent
from src.models.profiles import ProfileModel
from src.models.users import UserModel
from src.repositories.users import UserRepository
from src.schemas.profiles import ProfileCreate
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.exceptions.common import NotFoundError
import logging

from src.services.events.users import UserDeletedEvent

logger = logging.getLogger(__name__)


async def create_user(
    session: AsyncSession,
    data: UserCreate,
    producer: KafkaProducer,
) -> UserRead:
    repo = UserRepository(session)
    user = UserModel(
        id = uuid4(),
        name=data.name,
    )

    user_read = UserRead.model_validate(user)

    event = UserCreatedEvent(
        user_id=user_read.id,
        name=user_read.name,
    )

    await producer.publish(
        topic=settings.kafka.users_created_topic,
        payload=event.model_dump(),
    )

    await repo.create(user)

    return user_read


async def get_user(
    session: AsyncSession,
    user_id: UUID,
) -> UserRead:
    cache_key = f"user:{user_id}"

    cached = await redis.get(cache_key)
    if cached:
        return UserRead.model_validate_json(cached)

    repo = UserRepository(session)
    user = await repo.get_by_id(
        user_id,
    )

    if user is None:
        message = f"User with id {user_id} not found"
        logger.info(
            message,
            extra={"user_id": str(user_id)},
        )
        raise NotFoundError(message)

    data = UserRead.model_validate(user)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data


async def update_user(
    session: AsyncSession,
    user_id: UUID,
    data: UserUpdate,
    producer: KafkaProducer,
    profile_data: ProfileCreate | None = None,
) -> UserRead:
    repo = UserRepository(session)
    user = await repo.get_by_id(
        user_id,
    )

    if user is None:
        raise NotFoundError(f"User with id {user_id} not found")

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(user, key, value)

    if profile_data is not None:
        profile = ProfileModel(**profile_data.model_dump(exclude_unset=True))
        user.profile = profile

    data_read = UserRead.model_validate(user)

    event = UserUpdatedEvent(
        user_id=data_read.id,
        name=data_read.name,
    )

    await producer.publish(
        topic=settings.kafka.users_updated_topic,
        payload=event.model_dump(),
    )

    await redis.set(
        f"user:{user_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_user(
    session: AsyncSession,
    user_id: UUID,
    producer: KafkaProducer,
) -> None:
    repo = UserRepository(session)

    user = await repo.get_by_id(user_id)
    if user is None:
        logger.info(
            "User not found",
            extra={"user_id": str(user_id)},
        )
        raise NotFoundError(f"User with id {user_id} not found")

    await repo.delete_by_id(user_id)

    await redis.delete(f"user:{user_id}")

    event = UserDeletedEvent(
        user_id=user.id,
    )

    await producer.publish(
        topic=settings.kafka.users_deleted_topic,
        payload=event.model_dump(),
    )





