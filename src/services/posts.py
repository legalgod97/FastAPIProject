from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orders import OrderModel
from models.posts import PostModel
from schemas.posts import PostCreate, PostUpdate, PostRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_post(
    session: AsyncSession,
    data: PostCreate,
) -> PostRead:
    post: PostModel = PostModel(
        id=data.id or uuid4(),
        title=data.title,
        content=data.content,
    )

    if data.order:
        order = OrderModel(**data.order.model_dump(exclude_unset=True))
        post.order = order

    session.add(post)

    return PostRead.model_validate(post)


async def get_post(
    session: AsyncSession,
    post_id: UUID,
) -> PostRead:
    stmt = select(PostModel).where(PostModel.id == post_id).options(
        selectinload(PostModel.order))
    result = await session.execute(stmt)
    post = result.scalars().first()

    if post is None:
        raise NotFoundError("Post")

    return PostRead.model_validate(post)

async def update_post(
    session: AsyncSession,
    post_id: UUID,
    data: PostUpdate,
) -> PostRead:
    stmt = select(PostModel).where(PostModel.id == post_id).options(
        selectinload(PostModel.order))
    result = await session.execute(stmt)
    post = result.scalars().first()

    if post is None:
        logger.info(
            "Post not found",
            extra={"post_id": str(post_id)},
        )
        raise NotFoundError("Post")

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(post, key, value)

    return PostRead.model_validate(post)

async def delete_post(
    session: AsyncSession,
    post_id: UUID,
) -> None:
    stmt = select(PostModel).where(PostModel.id == post_id).options(
        selectinload(PostModel.order))
    result = await session.execute(stmt)
    post = result.scalars().first()

    if post is None:
        logger.info(
            "Post not found while deleting",
            extra={"post_id": str(post_id)},
        )
        raise NotFoundError("Post")

    await session.delete(post)

