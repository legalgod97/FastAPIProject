from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orders import OrderModel


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: OrderModel) -> None:
        self.session.add(order)

    async def get_by_id(
            self,
            order_id: UUID,
            *,
            with_post: bool = False,
            with_posts_m2m: bool = False,
    ) -> OrderModel | None:
        stmt = select(OrderModel).where(OrderModel.id == order_id)

        if with_post:
            stmt = stmt.options(selectinload(OrderModel.post))

        if with_posts_m2m:
            stmt = stmt.options(selectinload(OrderModel.posts_m2m))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, order: OrderModel) -> None:
        await self.session.delete(order)