from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from models.posts import PostModel
from schemas.posts import PostCreate, PostUpdate
from services.exceptions import NotFoundError


async def create_post(
    session: AsyncSession,
    data: PostCreate,
) -> PostModel:
    post: PostModel = PostModel(
        id=data.id or uuid4(),
        title=data.title,
        content=data.content,
    )

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return post

async def get_post(
    session: AsyncSession,
    post_id: UUID,
) -> PostModel:
    post: PostModel | None = await session.get(PostModel, post_id)

    if post is None:
        raise NotFoundError("Post")

    return post

async def update_post(
    session: AsyncSession,
    post_id: UUID,
    data: PostUpdate,
) -> PostModel:
    post: PostModel | None = await session.get(PostModel, post_id)

    if post is None:
        raise NotFoundError("Post")

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(post, key, value)

    await session.commit()
    await session.refresh(post)

    return post

async def delete_post(
    session: AsyncSession,
    post_id: UUID,
) -> PostModel:
    post: PostModel | None = await session.get(PostModel, post_id)

    if post is None:
        raise NotFoundError("Post")

    await session.delete(post)
    await session.commit()

    return post
