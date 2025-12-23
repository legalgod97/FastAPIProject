from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from config.redis import redis, CACHE_TTL
from models.profiles import ProfileModel
from repositories.profiles import ProfileRepository
from schemas.profiles import ProfileUpdate, ProfileRead, ProfileCreate
from exceptions.common import NotFoundError
import logging


logger = logging.getLogger(__name__)


async def create_profile(
    session: AsyncSession,
    data: ProfileCreate,
) -> ProfileRead:
    repo = ProfileRepository(session)

    profile = ProfileModel(
        id=data.id or uuid4(),
        full_name=data.full_name,
        bio=data.bio,
        owner_id=data.owner_id,
    )

    await repo.create(profile)

    return ProfileRead.model_validate(profile)


async def get_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileRead:
    cache_key = f"profile:{profile_id}"

    cached = await redis.get(cache_key)
    if cached:
        return ProfileRead.model_validate_json(cached)

    repo = ProfileRepository(session)
    profile = await repo.get_by_id(profile_id)

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
    repo = ProfileRepository(session)
    profile = await repo.get_by_id(profile_id)

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

    data_read = ProfileRead.model_validate(profile)

    await redis.set(
        f"profile:{profile_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> None:
    repo = ProfileRepository(session)
    profile = await repo.get_by_id(profile_id)

    if profile is None:
        logger.info(
            f"Profile with id {profile_id} not found",
            extra={"profile_id": str(profile_id)},
        )
        raise NotFoundError(f"Profile with id {profile_id} not found while deleting")

    await repo.delete(profile)

    await redis.delete(f"profile:{profile_id}")



