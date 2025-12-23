from uuid import UUID

from sqlalchemy import select
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
            *,
            with_orders: bool = False,
            with_orders_m2m: bool = False,
    ) -> PostModel | None:
        stmt = select(PostModel).where(PostModel.id == post_id)

        if with_orders:
            stmt = stmt.options(selectinload(PostModel.orders))

        if with_orders_m2m:
            stmt = stmt.options(selectinload(PostModel.orders_m2m))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, post: PostModel) -> None:
        await self.session.delete(post)