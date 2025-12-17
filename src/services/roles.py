from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.comments import CommentModel
from models.roles import RoleModel
from schemas.comments import CommentCreate
from schemas.roles import RoleCreate, RoleUpdate, RoleRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_role(
    session: AsyncSession,
    data: RoleCreate,
) -> RoleRead:
    payload = data.model_dump(exclude={"comment"}, exclude_unset=True)

    role = RoleModel(**payload)

    if data.comment:
        comment = CommentModel(**data.comment.model_dump(exclude_unset=True))
        role.comment = comment

    session.add(role)
    return RoleRead.model_validate(role)


async def get_role(
    session: AsyncSession,
    role_id: UUID,
) -> RoleModel:
    stmt = select(RoleModel).where(RoleModel.id == role_id)
    result = await session.execute(stmt)
    role = result.scalars().first()

    if role is None:
        logger.info(
            "Role not found",
            extra={"role_id": str(role_id)},
        )
        raise NotFoundError("Role")

    return role


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

    return RoleRead.model_validate(role)


async def delete_role(
    session: AsyncSession,
    role_id: UUID,
) -> None:
    role = await get_role(session, role_id)
    await session.delete(role)
