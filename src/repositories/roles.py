from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.roles import RoleModel


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: RoleModel) -> None:
        self.session.add(role)

    async def get_by_id(
            self,
            role_id: UUID,
            *,
            with_main_comment: bool = False,
            with_comments: bool = False,
            with_shared_comments: bool = False,
    ) -> RoleModel | None:
        stmt = select(RoleModel).where(RoleModel.id == role_id)

        if with_main_comment:
            stmt = stmt.options(selectinload(RoleModel.main_comment))

        if with_comments:
            stmt = stmt.options(selectinload(RoleModel.comments))

        if with_shared_comments:
            stmt = stmt.options(selectinload(RoleModel.shared_comments))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, role: RoleModel) -> None:
        await self.session.delete(role)