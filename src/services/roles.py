from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comments import CommentModel
from models.roles import RoleModel
from schemas.comments import CommentCreate
from schemas.roles import RoleCreate, RoleUpdate, RoleRead
from services.exceptions import NotFoundError


async def create_role(
    session: AsyncSession,
    data: RoleCreate,
    comment_data: CommentCreate | None = None,
) -> RoleRead:
    role = RoleModel(**data.model_dump(exclude_unset=True))

    if comment_data:
        comment = CommentModel(**comment_data.model_dump(exclude_unset=True))
        role.comment = comment
        session.add(comment)

    session.add(role)

    return RoleRead.model_validate(role)


async def get_role(
    session: AsyncSession,
    role_id: UUID,
) -> RoleRead:
    stmt = select(RoleModel).where(RoleModel.id == role_id).options(
        selectinload(RoleModel.main_comment))
    result = await session.execute(stmt)
    role: RoleModel | None = result.scalars().first()

    if role is None:
        raise NotFoundError("Role")
    return RoleRead.model_validate(role)


async def update_role(
    session: AsyncSession,
    role_id: UUID,
    data: RoleUpdate,
    comment_data: CommentCreate | None = None,
) -> RoleRead:
    role = await get_role(session, role_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(role, key, value)

    if comment_data:
        comment = CommentModel(**comment_data.model_dump(exclude_unset=True))
        role.main_comment = comment
        session.add(comment)

    return RoleRead.model_validate(role)


async def delete_role(
    session: AsyncSession,
    role_id: UUID,
) -> None:
    role = await get_role(session, role_id)
    await session.delete(role)
