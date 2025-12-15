from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import UserModel
from schemas.users import UserCreate
from services.exceptions import NotFoundError


async def create_user(
    session: AsyncSession,
    data: UserCreate,
) -> UserModel:
    user = UserModel(
        id=data.id or uuid4(),
        name=data.name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(
    session: AsyncSession,
    user_id: UUID,
) -> UserModel:
    user: Optional[UserModel] = await session.get(UserModel, user_id)

    if user is None:
        raise NotFoundError("Post")

    return user


async def update_user(
    session: AsyncSession,
    user_id: UUID,
    data: UserCreate,
) -> UserModel:
    user = await get_user(session, user_id)
    user.name = data.name
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    session: AsyncSession,
    user_id: UUID,
) -> None:
    user = await get_user(session, user_id)
    await session.delete(user)
    await session.commit()
