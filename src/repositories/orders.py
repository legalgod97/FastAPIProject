from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orders import OrderModel


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: OrderModel) -> None:
        self.session.add(order)

    async def get_by_id(
            self,
            order_id: UUID,
    ) -> OrderModel | None:
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(
                selectinload(OrderModel.post),
                selectinload(OrderModel.posts_m2m),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_by_id(self, order_id: UUID) -> None:
        stmt = delete(OrderModel).where(OrderModel.id == order_id)
        await self.session.execute(stmt)