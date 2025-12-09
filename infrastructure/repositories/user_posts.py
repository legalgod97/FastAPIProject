from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infrastructure.db.models.posts import PostModel
from infrastructure.db.models.users import UserModel


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user_with_posts(data: dict, session: AsyncSession):
    user_data = data["user"]
    posts_data = data.get("posts", [])

    user = UserModel(
        id=user_data.get("id", uuid4()),
        title=user_data["title"],
    )

    user_posts = []
    for post in posts_data:
        new_post = PostModel(
            id=post.get("id", uuid4()),
            author_id=post.get("author_id", uuid4()),
            title=post["title"],
            content=post["content"],
            is_published=post.get("is_published", False),
            published_at=post.get("published_at"),
        )
        user_posts.append(new_post)

    user.posts = user_posts

    session.add(user)
    await session.commit()

    return {
        "user_id": str(user.id),
        "posts_ids": [str(post.id) for post in user.posts]
    }

@router.get("/{user_id}")
async def get_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.posts))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    posts_list = []
    for post in user.posts:
        post_dict = {
            "id": str(post.id),
            "author_id": str(post.author_id),
            "title": post.title,
            "content": post.content,
            "is_published": post.is_published,
            "published_at": post.published_at.isoformat() if post.published_at else None,
        }
        posts_list.append(post_dict)

    return {
        "user": {
            "id": str(user.id),
            "title": user.title,
        },
        "posts": posts_list
    }


@router.put("/{user_id}")
async def update_user(user_id: UUID, data: dict, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.posts))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    user_data = data["user"]
    posts_data = data.get("posts", [])

    user.title = user_data["title"]

    user_posts = []
    for post in posts_data:
        new_post = PostModel(
            id=post.get("id", uuid4()),
            author_id=post.get("author_id", uuid4()),
            title=post["title"],
            content=post["content"],
            is_published=post.get("is_published", False),
            published_at=post.get("published_at"),
        )
        user_posts.append(new_post)

    user.posts = user_posts

    await session.commit()
    return {"status": "updated"}

@router.delete("/{post_id}")
async def delete_post(post_id: UUID, session: AsyncSession):
    query = select(PostModel).where(PostModel.id == post_id)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    await session.delete(post)
    await session.commit()

    return {"status": "deleted", "post_id": str(post_id)}

@router.delete("/{user_id}")
async def delete_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.posts))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return {"status": "deleted"}
