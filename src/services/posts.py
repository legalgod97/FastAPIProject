from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.redis import redis, CACHE_TTL
from src.models.posts import PostModel
from src.repositories.posts import PostRepository
from src.schemas.posts import PostCreate, PostUpdate, PostRead
from src.exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_post(
    session: AsyncSession,
    data: PostCreate,
) -> PostRead:
    repo = PostRepository(session)

    post: PostModel = PostModel(
        id=uuid4(),
        title=data.title,
        content=data.content,
    )

    await repo.create(post)

    return PostRead.model_validate(post)


async def get_post(
    session: AsyncSession,
    post_id: UUID,
) -> PostRead:
    cache_key = f"post:{post_id}"

    cached = await redis.get(cache_key)
    if cached:
        return PostRead.model_validate_json(cached)

    repo = PostRepository(session)
    post = await repo.get_by_id(post_id)

    if post is None:
        raise NotFoundError(f"Post with id {post_id} not found")

    data = PostRead.model_validate(post)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data


async def update_post(
    session: AsyncSession,
    post_id: UUID,
    data: PostUpdate,
) -> PostRead:
    repo = PostRepository(session)
    post = await repo.get_by_id(post_id)

    if post is None:
        message = f"Post with id {post_id} not found"
        logger.info(
            message,
            extra={"post_id": str(post_id)},
        )
        raise NotFoundError(message)

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(post, key, value)

    data_read = PostRead.model_validate(post)

    await redis.set(
        f"post:{post_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_post(
    session: AsyncSession,
    post_id: UUID,
) -> None:
    repo = PostRepository(session)
    post = await repo.get_by_id(post_id)

    if post is None:
        logger.info(
            f"Post with id {post_id} not found",
            extra={"post_id": str(post_id)},
        )
        raise NotFoundError(f"Post with id {post_id} not found")

    await redis.delete(f"post:{post_id}")

    await repo.delete_by_id(post_id)





