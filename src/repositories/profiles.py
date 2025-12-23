from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.profiles import ProfileModel


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: ProfileModel) -> None:
        self.session.add(profile)

    async def get_by_id(
            self,
            profile_id: UUID,
    ) -> ProfileModel | None:
        stmt = select(ProfileModel).where(ProfileModel.id == profile_id)


        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, profile: ProfileModel) -> None:
        await self.session.delete(profile)