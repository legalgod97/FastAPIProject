from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from config.redis import redis, CACHE_TTL
from models.comments import CommentModel
from repositories.comments import CommentRepository
from schemas.comments import CommentCreate, CommentUpdate, CommentRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_comment(
    session: AsyncSession,
    data: CommentCreate,
) -> CommentRead:
    repo = CommentRepository(session)

    comment = CommentModel(
        id=uuid4(),
        content=data.content,
    )

    await repo.create(comment)

    return CommentRead.model_validate(comment)



async def get_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> CommentRead:
    cache_key = f"comment:{comment_id}"

    cached = await redis.get(cache_key)
    if cached:
        return CommentRead.model_validate_json(cached)

    repo = CommentRepository(session)
    comment = await repo.get_by_id(comment_id, with_role=True)

    if comment is None:
        raise NotFoundError(f"Comment with id={comment_id} not found")

    data = CommentRead.model_validate(comment)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data


async def update_comment(
    session: AsyncSession,
    comment_id: UUID,
    data: CommentUpdate,
) -> CommentRead:
    repo = CommentRepository(session)
    comment = await repo.get_by_id(comment_id, with_role=True)

    if comment is None:
        message = f"Comment with id={comment_id} not found"
        logger.info(
            message,
            extra={"comment_id": str(comment_id)},
        )
        raise NotFoundError(message)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(comment, key, value)

        comment.is_edited = True

    return CommentRead.model_validate(comment)


async def delete_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> None:
    repo = CommentRepository(session)

    comment = await repo.get_by_id(comment_id, with_role=True)

    if comment is None:
        logger.info(
            f"Comment with id={comment_id} not found",
            extra={"comment_id": str(comment_id)},
        )
        raise NotFoundError(f"Comment with id {comment_id} not found")

    await repo.delete(comment)

