from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.users import UserCreate
from services.users import (
    create_user,
    get_user,
    update_user,
    delete_user,
)

router = APIRouter(prefix="/users", tags=["users"])


# CREATE
@router.post("/")
async def create_user_route(
    data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    user = await create_user(session, data)
    return {
        "id": str(user.id),
        "name": user.name,
    }


# READ
@router.get("/{user_id}")
async def get_user_route(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_user(session, user_id)
    return {
        "id": str(user.id),
        "name": user.name,
    }


# UPDATE
@router.put("/{user_id}")
async def update_user_route(
    user_id: UUID,
    data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    user = await update_user(session, user_id, data)
    return {
        "id": str(user.id),
        "name": user.name,
    }


# DELETE
@router.delete("/{user_id}")
async def delete_user_route(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_user(session, user_id)
    return {"status": "deleted"}
