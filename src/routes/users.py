from uuid import uuid4, UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from models.users import UserModel
from schemas.users import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    user = UserModel(
        id=data.id or uuid4(),
        name=data.name,
    )

    session.add(user)
    await session.commit()

    return {"id": str(user.id), "name": user.name}


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return {"id": str(user.id), "name": user.name}


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    user.name = data.name
    await session.commit()

    return {"status": "updated"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return {"status": "deleted"}
