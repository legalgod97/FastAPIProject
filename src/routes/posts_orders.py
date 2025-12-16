from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.common import DeleteResult
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


@router.post("/", response_model=PostRead)
async def create_post_route(
    data: PostCreate,
    session: AsyncSession = Depends(get_async_session),
):
    post = await create_post(session, data)
    return post


@router.get("/{post_id}", response_model=PostRead)
async def get_post_route(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    post = await get_post(session, post_id)
    return post


@router.put("/{post_id}", response_model=PostRead)
async def update_post_route(
    post_id: UUID,
    data: PostUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    post = await update_post(session, post_id, data)
    return post


@router.delete("/{post_id}", response_model=DeleteResult)
async def delete_post_route(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_post(session, post_id)
    return DeleteResult(status="deleted")
