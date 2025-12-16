from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comments import CommentModel
from models.roles import RoleModel
from schemas.comments import CommentCreate, CommentUpdate, CommentRead
from schemas.roles import RoleCreate, RoleRead
from services.exceptions import NotFoundError


async def create_comment(
    session: AsyncSession,
    data: CommentCreate,
    role_data: RoleCreate | None = None,
) -> CommentRead:
    comment = CommentModel(
        id=uuid4(),
        **data.model_dump(exclude_unset=True),
    )

    if role_data:
        role = RoleModel(**role_data.model_dump(exclude_unset=True))
        comment.role = role
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
    comment: CommentModel | None = result.scalars().first()

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
    comment: CommentModel | None = result.scalars().first()

    if comment is None:
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
    comment: CommentModel | None = result.scalars().first()

    if comment is None:
        raise NotFoundError("Comment")

    await session.delete(comment)