from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.roles import RoleModel


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: RoleModel) -> RoleModel:
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def get_by_id(self, role_id: UUID) -> RoleModel | None:
        stmt = (
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(
                selectinload(RoleModel.main_comment),
                selectinload(RoleModel.comments),
                selectinload(RoleModel.shared_comments),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def delete_by_id(self, role_id: UUID) -> None:
        stmt = delete(RoleModel).where(RoleModel.id == role_id)
        await self.session.execute(stmt)

