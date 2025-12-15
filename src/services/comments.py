from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from models.comments import CommentModel
from schemas.comments import CommentCreate, CommentUpdate
from services.exceptions import NotFoundError


async def create_comment(
    session: AsyncSession,
    data: CommentCreate,
) -> CommentModel:
    comment: CommentModel = CommentModel(
        id=uuid4(),
        **data.model_dump(exclude_unset=True),
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return comment


async def get_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> CommentModel:
    comment: CommentModel | None = await session.get(CommentModel, comment_id)

    if comment is None:
        raise NotFoundError("Comment")

    return comment

async def update_comment(
    session: AsyncSession,
    comment_id: UUID,
    data: CommentUpdate,
) -> CommentModel:
    comment: CommentModel | None = await session.get(CommentModel, comment_id)

    if comment is None:
        raise NotFoundError("Comment")

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(comment, key, value)

    if "content" in payload:
        comment.is_edited = True

    await session.commit()
    await session.refresh(comment)

    return comment

async def delete_comment(
    session: AsyncSession,
    comment_id: UUID,
) -> CommentModel:
    comment: CommentModel | None = await session.get(CommentModel, comment_id)

    if comment is None:
        raise NotFoundError("Comment")

    await session.delete(comment)
    await session.commit()

    return comment