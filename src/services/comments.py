from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comments import CommentModel
from models.roles import RoleModel
from schemas.comments import CommentCreate, CommentUpdate, CommentRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_comment(
    session: AsyncSession,
    data: CommentCreate,
) -> CommentRead:
    comment = CommentModel(
        id=uuid4(),
        content=data.content,
    )

    if data.role:
        role = RoleModel(**data.role.model_dump(exclude_unset=True))
        comment.role_o2o = role
        session.add(role)

    session.add(comment)
    return CommentRead.model_validate(comment)



async def get_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> CommentRead:
    stmt = select(CommentModel).where(CommentModel.id == comment_id).options(
        selectinload(CommentModel.role_o2o)
    )
    result = await session.execute(stmt)
    comment = result.scalars().first()

    if comment is None:
        raise NotFoundError("Comment")

    return CommentRead.model_validate(comment)


async def update_comment(
    session: AsyncSession,
    comment_id: UUID,
    data: CommentUpdate,
) -> CommentRead:
    stmt = select(CommentModel).where(CommentModel.id == comment_id).options(
        selectinload(CommentModel.role_o2o))
    result = await session.execute(stmt)
    comment = result.scalars().first()

    if comment is None:
        logger.info(
            "Comment not found",
            extra={"comment_id": str(comment_id)},
        )
        raise NotFoundError("Comment")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(comment, key, value)

        comment.is_edited = True

    return CommentRead.model_validate(comment)


async def delete_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> None:
    stmt = select(CommentModel).where(CommentModel.id == comment_id).options(
        selectinload(CommentModel.role_o2o))
    result = await session.execute(stmt)
    comment = result.scalars().first()

    if comment is None:
        logger.info(
            "Comment not found while deleting",
            extra={"comment_id": str(comment_id)},
        )
        raise NotFoundError("Comment")

    await session.delete(comment)