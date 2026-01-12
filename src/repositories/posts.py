from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.posts import PostModel


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post: PostModel) -> None:
        self.session.add(post)

    async def get_by_id(
            self,
            post_id: UUID,
    ) -> PostModel | None:
        stmt = (
            select(PostModel)
            .where(PostModel.id == post_id)
            .options(
                selectinload(PostModel.orders),
                selectinload(PostModel.orders_m2m),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, post_id: UUID) -> None:
        stmt = delete(PostModel).where(PostModel.id == post_id)
        await self.session.execute(stmt)