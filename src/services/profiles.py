from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.profiles import ProfileModel
from models.users import UserModel
from schemas.profiles import ProfileCreate, ProfileUpdate, ProfileRead
from schemas.users import UserCreate
from services.exceptions import NotFoundError


async def create_profile(
    session: AsyncSession,
    data: ProfileCreate,
    user_data: UserCreate | None = None,
) -> ProfileRead:
    payload: dict = data.model_dump(exclude_unset=True)

    profile: ProfileModel = ProfileModel(**payload)

    if user_data:
        user = UserModel(**user_data.model_dump(exclude_unset=True))
        profile.owner = user
        session.add(user)

    session.add(profile)

    return ProfileRead.model_validate(profile)

async def get_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileRead:
    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile: ProfileModel | None = result.scalars().first()

    if profile is None:
        raise NotFoundError("Profile")

    return ProfileRead.model_validate(profile)


async def update_profile(
    session: AsyncSession,
    profile_id: UUID,
    data: ProfileUpdate,
) -> ProfileRead:
    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile: ProfileModel | None = result.scalars().first()

    if profile is None:
        raise NotFoundError("Profile")

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
        raise NotFoundError("Post")

    await session.delete(profile)

