from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.redis import redis, CACHE_TTL
from src.models.comments import CommentModel
from src.models.roles import RoleModel
from src.repositories.roles import RoleRepository
from src.schemas.comments import CommentCreate
from src.schemas.roles import RoleCreate, RoleUpdate, RoleRead
from src.exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_role(
    session: AsyncSession,
    data: RoleCreate,
) -> RoleRead:
    repo = RoleRepository(session)
    payload = data.model_dump(exclude={"comment"}, exclude_unset=True)

    role = RoleModel(**payload)

    await repo.create(role)

    return RoleRead.model_validate(role)


async def get_role(
    session: AsyncSession,
    role_id: UUID,
) -> RoleRead:
    cache_key = f"role:{role_id}"

    cached = await redis.get(cache_key)
    if cached:
        return RoleRead.model_validate_json(cached)

    repo = RoleRepository(session)
    role = await repo.get_by_id(
        role_id,
    )

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
    repo = RoleRepository(session)
    role = await repo.get_by_id(
        role_id,
    )

    if role is None:
        raise NotFoundError(f"Role with id {role_id} not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(role, key, value)

    if comment_data:
        comment = CommentModel(**comment_data.model_dump(exclude_unset=True))
        role.main_comment = comment

    data_read = RoleRead.model_validate(role)

    await redis.set(
        f"role:{role_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_role(
    session: AsyncSession,
    role_id: UUID,
) -> None:
    repo = RoleRepository(session)
    role = await repo.get_by_id(role_id)

    if role is None:
        logger.info(
            f"Role with id {role_id} not found",
            extra={"role_id": str(role_id)},
        )
        raise NotFoundError(f"Role with id {role_id} not found")

    await redis.delete(f"role:{role_id}")

    await repo.delete_by_id(role_id)








