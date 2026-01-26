from uuid import UUID
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from src.schemas.users import UserCreate, UserUpdate, UserRead
from src.services.users import (
    create_user,
    get_user,
    update_user,
    delete_user,
)

router = APIRouter(
    prefix="/v1/users_profiles",
    tags=["v1", "users_profiles"],
)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_handler(
    data: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_user(session, data, producer=request.app.state.kafka_producer)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_handler(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_user(session, user_id)


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user_handler(
    user_id: UUID,
    data: UserUpdate,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_user(session, user_id, data, producer=request.app.state.kafka_producer)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_handler(
    user_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_user(session, user_id, producer=request.app.state.kafka_producer)
