from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.profiles import ProfileModel
from schemas.profiles import ProfileCreate, ProfileUpdate
from services.exceptions import NotFoundError


async def create_profile(
    session: AsyncSession,
    data: ProfileCreate,
) -> ProfileModel:
    payload: dict = data.model_dump(exclude_unset=True)

    profile: ProfileModel = ProfileModel(**payload)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    return profile

async def get_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileModel:
    profile: ProfileModel | None = await session.get(ProfileModel, profile_id)

    if profile is None:
        raise NotFoundError("Post")

    return profile

async def list_profiles(
    session: AsyncSession,
) -> list[ProfileModel]:
    result = await session.execute(select(ProfileModel))
    profiles = list(result.scalars().all())
    return profiles

async def update_profile(
    session: AsyncSession,
    profile_id: UUID,
    data: ProfileUpdate,
) -> ProfileModel:
    profile: ProfileModel | None = await session.get(ProfileModel, profile_id)

    if profile is None:
        raise NotFoundError("Post")

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(profile, key, value)

    await session.commit()
    await session.refresh(profile)

    return profile

async def delete_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileModel:
    profile: ProfileModel | None = await session.get(ProfileModel, profile_id)

    if profile is None:
        raise NotFoundError("Post")

    await session.delete(profile)
    await session.commit()

    return profile