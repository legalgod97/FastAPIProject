from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.posts import PostModel
from models.comments import CommentModel

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/")
async def create_post_with_comments(data: dict, session: AsyncSession):
    post_data = data["post"]
    comments_data = data.get("comments", [])

    post = PostModel(
        id=post_data.get("id", uuid4()),
        author_id=post_data["author_id"],
        title=post_data["title"],
        content=post_data["content"],
        is_published=post_data["is_published"],
        published_at=post_data["published_at"],
    )

    post_comments = []
    for comment in comments_data:
        new_comment = CommentModel(
            id=comment.get("id", uuid4()),
            author_id=comment["author_id"],
            content=comment["content"],
            is_edited=comment["is_edited"],
        )
        post_comments.append(new_comment)

    post.comments = post_comments

    session.add(post)
    await session.commit()

    return {
        "post_id": str(post.id),
        "comments_ids": [str(comment.id) for comment in post.comments]
    }


@router.get("/{post_id}")
async def get_post(post_id: UUID, session: AsyncSession):
    query = (
        select(PostModel)
        .where(PostModel.id == post_id)
        .options(selectinload(PostModel.comments))
    )
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    comments_list = []
    for comment in post.comments:
        comment_dict = {
            "id": str(comment.id),
            "author_id": str(comment.author_id),
            "content": comment.content,
            "is_edited": comment.is_edited,
        }
        comments_list.append(comment_dict)

    return {
        "post": {
            "id": str(post.id),
            "title": post.title,
        },
        "comments": comments_list
    }

@router.put("/{post_id}")
async def update_post(post_id: UUID, data: dict, session: AsyncSession):
    query = (
        select(PostModel)
        .where(PostModel.id == post_id)
        .options(selectinload(PostModel.comments))
    )
    post = (await session.execute(query)).scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    post_data = data["post"]
    post.title = post_data["title"]

    comments_data = data.get("comments", [])

    post.comments.clear()

    for comment in comments_data:
        post.comments.append(
            CommentModel(
                id=comment.get("id", uuid4()),
                author_id=comment["author_id"],
                content=comment["content"],
                is_edited=comment["is_edited"],  # пока оставляем
            )
        )

    await session.commit()
    return {"status": "updated"}

@router.delete("/{comment_id}")
async def delete_comment(comment_id: UUID, session: AsyncSession):
    query = select(CommentModel).where(CommentModel.id == comment_id)
    result = await session.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(404, "Comment not found")

    await session.delete(comment)
    await session.commit()

    return {
        "status": "deleted",
        "comment_id": str(comment_id)
    }

@router.delete("/{post_id}")
async def delete_post(post_id: UUID, session: AsyncSession):
    query = (
        select(PostModel)
        .where(PostModel.id == post_id)
        .options(selectinload(PostModel.comments))
    )
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    await session.delete(post)
    await session.commit()

    return {
        "status": "deleted",
        "post_id": str(post_id)
    }
