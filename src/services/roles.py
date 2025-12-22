from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.redis import redis, CACHE_TTL
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

    session.add(role)
    return RoleRead.model_validate(role)


async def get_role(
    session: AsyncSession,
    role_id: UUID,
) -> RoleRead:
    cache_key = f"role:{role_id}"

    cached = await redis.get(cache_key)
    if cached:
        return RoleRead.model_validate_json(cached)

    stmt = select(RoleModel).where(RoleModel.id == role_id)
    result = await session.execute(stmt)
    role = result.scalars().first()

    if role is None:
        message = f"Role with id {role_id} not found"
        logger.info(
            message,
            extra={"role_id": str(role_id)},
        )
        raise NotFoundError(message)

    data = RoleRead.model_validate(role)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data



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
