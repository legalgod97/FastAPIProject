from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.users import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserModel) -> None:
        self.session.add(user)

    async def get_by_id(
            self,
            user_id: UUID,
    ) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.profiles),
                selectinload(UserModel.many_profiles),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, user_id: UUID) -> None:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await self.session.execute(stmt)