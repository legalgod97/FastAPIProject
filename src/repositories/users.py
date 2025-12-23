from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.users import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserModel) -> None:
        self.session.add(user)

    async def get_by_id(
            self,
            user_id: UUID,
            *,
            with_profile: bool = False,
            with_profiles: bool = False,
            with_many_profiles: bool = False,
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)

        if with_profile:
            stmt = stmt.options(selectinload(UserModel.profile))

        if with_profiles:
            stmt = stmt.options(selectinload(UserModel.profiles))

        if with_many_profiles:
            stmt = stmt.options(selectinload(UserModel.many_profiles))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, user: UserModel) -> None:
        await self.session.delete(user)