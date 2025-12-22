from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.posts import PostCreate, PostUpdate, PostRead
from services.posts import (
    create_post,
    get_post,
    update_post,
    delete_post,
)

router = APIRouter(
    prefix="/v1/posts_orders",
    tags=["v1", "posts_orders"],
)


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post_handler(
    data: PostCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_post(session, data)


@router.get("/{post_id}", response_model=PostRead, status_code=status.HTTP_200_OK)
async def get_post_handler(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_post(session, post_id)


@router.put("/{post_id}", response_model=PostRead, status_code=status.HTTP_200_OK)
async def update_post_handler(
    post_id: UUID,
    data: PostUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_post(session, post_id, data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_handler(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_post(session, post_id)

