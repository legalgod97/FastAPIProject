from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    if data.profile:
        user.profile = ProfileModel(
            **data.profile.model_dump(exclude_unset=True)
        )

    session.add(user)
    return UserRead.model_validate(user)


async def get_profile(
    session: AsyncSession,
    profile_id: UUID,
) -> ProfileRead:
    stmt = select(ProfileModel).where(ProfileModel.id == profile_id).options(
        selectinload(ProfileModel.owner))
    result = await session.execute(stmt)
    profile = result.scalars().first()

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
    profile = result.scalars().first()

    if profile is None:
        logger.info(
            "Profile not found",
            extra={"profile_id": str(profile_id)},
        )
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
        logger.info(
            "Profile not found while deleting",
            extra={"profile_id": str(profile_id)},
        )
        raise NotFoundError("Profile")

    await session.delete(profile)

