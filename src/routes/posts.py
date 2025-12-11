from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from models.posts import PostModel
from schemas.posts import PostCreate, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


# CREATE
@router.post("/")
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_async_session)
):
    post = PostModel(
        id=data.id or uuid4(),
        title=data.title,
        content=data.content,
    )

    session.add(post)
    await session.commit()

    return {"id": str(post.id)}


# READ
@router.get("/{post_id}")
async def get_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    return {
        "id": str(post.id),
        "title": post.title,
        "content": post.content,
    }


# UPDATE
@router.put("/{post_id}")
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content

    await session.commit()
    return {"status": "updated"}


# DELETE
@router.delete("/{post_id}")
async def delete_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    await session.delete(post)
    await session.commit()

    return {"status": "deleted"}
