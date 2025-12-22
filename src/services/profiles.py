from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.redis import redis, CACHE_TTL
from models.profiles import ProfileModel
from models.users import UserModel
from schemas.profiles import ProfileUpdate, ProfileRead
from schemas.users import UserCreate, UserRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_user(
    session: AsyncSession,
    data: UserCreate,
) -> UserRead:
    user = UserModel(
        id=uuid4(),
        name=data.name,
    )

    session.add(user)
    return UserRead.model_validate(user)


async def get_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileRead:
    cache_key = f"profile:{profile_id}"

    cached = await redis.get(cache_key)
    if cached:
        return ProfileRead.model_validate_json(cached)

    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile = result.scalars().first()

    if profile is None:
        raise NotFoundError(f"Profile with id {profile_id} not found")

    data = ProfileRead.model_validate(profile)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data


async def update_profile(
    session: AsyncSession,
    profile_id: UUID,
    data: ProfileUpdate,
) -> ProfileRead:
    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile = result.scalars().first()

    if profile is None:
        message = f"Profile with id {profile_id} not found"
        logger.info(
            message,
            extra={"profile_id": str(profile_id)},
        )
        raise NotFoundError(message)

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(profile, key, value)

    return ProfileRead.model_validate(profile)

async def delete_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> None:
    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile: ProfileModel | None = result.scalars().first()

    if profile is None:
        logger.info(
            f"Profile with id {profile_id} not found while deleting",
            extra={"profile_id": str(profile_id)},
        )
        raise NotFoundError(f"Profile with id {profile_id} not found while deleting")

    await session.delete(profile)

