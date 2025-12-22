from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.profiles import ProfileModel
from models.users import UserModel
from schemas.profiles import ProfileCreate
from schemas.users import UserCreate, UserRead, UserUpdate
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_user(
    session: AsyncSession,
    data: UserCreate,
) -> UserRead:
    user = UserModel(
        id=data.id or uuid4(),
        name=data.name,
    )

    session.add(user)
    return UserRead.model_validate(user)


async def get_user(
    session: AsyncSession,
    user_id: UUID,
) -> UserRead:
    stmt = select(UserModel).where(UserModel.id == user_id).options(
        selectinload(UserModel.profile))
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        message = f"User with id {user_id} not found"
        logger.info(
            message,
            extra={"user_id": str(user_id)},
        )
        raise NotFoundError(message)

    return UserRead.model_validate(user)


async def update_user(
    session: AsyncSession,
    user_id: UUID,
    data: UserUpdate,
    profile_data: ProfileCreate | None = None,
) -> UserRead:
    user = await get_user(session, user_id)
    user.name = data.name

    if profile_data:
        profile = ProfileModel(**profile_data.model_dump(exclude_unset=True))
        user.profile = profile
        session.add(profile)

    return UserRead.model_validate(user)


async def delete_user(
    session: AsyncSession,
    user_id: UUID,
) -> None:
    user = await get_user(session, user_id)
    await session.delete(user)

