from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from config.redis import redis, CACHE_TTL
from models.profiles import ProfileModel
from models.users import UserModel
from repositories.users import UserRepository
from schemas.profiles import ProfileCreate
from schemas.users import UserCreate, UserRead, UserUpdate
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_user(
    session: AsyncSession,
    data: UserCreate,
) -> UserRead:
    repo = UserRepository(session)
    user = UserModel(
        id=data.id or uuid4(),
        name=data.name,
    )

    await repo.create(user)

    return UserRead.model_validate(user)


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
        with_profile=True,
        with_profiles=True,
        with_many_profiles=True,
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
    profile_data: ProfileCreate | None = None,
) -> UserRead:
    repo = UserRepository(session)
    user = await repo.get_by_id(
        user_id,
        with_profiles=True,
        with_many_profiles=True,
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

    await redis.set(
        f"user:{user_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_user(
    session: AsyncSession,
    user_id: UUID,
) -> None:
    repo = UserRepository(session)
    user = await repo.get_by_id(
        user_id,
        with_profile=True,
        with_profiles=True,
        with_many_profiles=True,
    )

    if user is None:
        logger.info(
            f"User with id {user_id} not found",
            extra={"user_id": str(user_id)},
        )
        raise NotFoundError(f"User with id {user_id} not found")

    await repo.delete(user)

    await redis.delete(f"user:{user_id}")



