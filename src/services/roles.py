from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from models.roles import RoleModel
from schemas.roles import RoleCreate, RoleUpdate
from services.exceptions import NotFoundError


async def create_role(
    session: AsyncSession,
    data: RoleCreate,
) -> RoleModel:
    role = RoleModel(**data.model_dump(exclude_unset=True))
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


async def get_role(
    session: AsyncSession,
    role_id: UUID,
) -> RoleModel:
    role: Optional[RoleModel] = await session.get(RoleModel, role_id)

    if role is None:
        raise NotFoundError("Post")
    return role


async def update_role(
    session: AsyncSession,
    role_id: UUID,
    data: RoleUpdate,
) -> RoleModel:
    role = await get_role(session, role_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(role, key, value)

    await session.commit()
    await session.refresh(role)
    return role


async def delete_role(
    session: AsyncSession,
    role_id: UUID,
) -> None:
    role = await get_role(session, role_id)
    await session.delete(role)
    await session.commit()