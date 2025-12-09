from fastapi import APIRouter, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from infrastructure.db.models.users import UserModel
from infrastructure.db.models.posts import PostModel, post_like

router = APIRouter(prefix="/posts", tags=["post_likes"])


@router.post("/likes")
async def create_like(data: dict, session: AsyncSession):

    post_id = UUID(data["post_id"])
    user_id = UUID(data["user_id"])

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    user = (await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    existing = (await session.execute(
        select(post_like).where(
            and_(
                post_like.c.post_id == post_id,
                post_like.c.user_id == user_id
            )
        )
    )).first()

    if existing:
        raise HTTPException(400, "Like already exists")

    await session.execute(
        post_like.insert().values(
            post_id=post_id,
            user_id=user_id
        )
    )
    await session.commit()

    return {"status": "created"}


@router.get("/{post_id}/likes")
async def get_post_likes(post_id: UUID, session: AsyncSession):

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    rows = (await session.execute(
        select(post_like.c.user_id).where(
            and_(post_like.c.post_id == post_id)
        )
    )).scalars().all()

    return {
        "post_id": str(post_id),
        "liked_by": [str(user_id) for user_id in rows]
    }


@router.get("/likes/user/{user_id}")
async def get_user_likes(user_id: UUID, session: AsyncSession):

    user = (await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    rows = (await session.execute(
        select(post_like.c.post_id).where(
            and_(post_like.c.user_id == user_id)
        )
    )).scalars().all()

    return {
        "user_id": str(user_id),
        "liked_posts": [str(post_id) for post_id in rows]
    }


@router.delete("/likes")
async def delete_like(data: dict, session: AsyncSession):

    post_id = UUID(data["post_id"])
    user_id = UUID(data["user_id"])

    existing = (await session.execute(
        select(post_like).where(
            and_(
                post_like.c.post_id == post_id,
                post_like.c.user_id == user_id
            )
        )
    )).first()

    if not existing:
        raise HTTPException(404, "Like not found")

    await session.execute(
        post_like.delete().where(
            and_(
                post_like.c.post_id == post_id,
                post_like.c.user_id == user_id
            )
        )
    )
    await session.commit()

    return {"status": "deleted"}
