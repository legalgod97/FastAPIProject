from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orders import OrderModel
from models.posts import PostModel
from schemas.orders import OrderCreate, OrderUpdate, OrderRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_order(
    session: AsyncSession,
    data: OrderCreate,
) -> OrderRead:
    order = OrderModel(
        id=data.id or uuid4(),
        price=data.price,
    )

    if data.post:
        post = PostModel(**data.post.model_dump(exclude_unset=True))
        order.post = post

    session.add(order)

    return OrderRead.model_validate(order)


async def get_order(
    session: AsyncSession,
    order_id: UUID,
) -> OrderRead:
    stmt = select(OrderModel).where(OrderModel.id == order_id).options(
        selectinload(OrderModel.post))
    result = await session.execute(stmt)
    order = result.scalars().first()

    if order is None:
        raise NotFoundError("Order")

    return OrderRead.model_validate(order)


async def update_order(
    session: AsyncSession,
    order_id: UUID,
    data: OrderUpdate,
) -> OrderRead:
    stmt = select(OrderModel).where(OrderModel.id == order_id).options(
        selectinload(OrderModel.post)
    )
    result = await session.execute(stmt)
    order = result.scalars().first()


    if order is None:
        logger.info(
            "Order not found",
            extra={"order_id": str(order_id)},
        )
        raise NotFoundError("Order")

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(order, key, value)

    return OrderRead.model_validate(order)


async def delete_order(
    session: AsyncSession,
    order_id: UUID,
) -> None:
    stmt = select(OrderModel).where(OrderModel.id == order_id).options(
        selectinload(OrderModel.post)
    )
    result = await session.execute(stmt)
    order = result.scalars().first()

    if order is None:
        logger.info(
            "Order not found while deleting",
            extra={"order_id": str(order_id)},
        )
        raise NotFoundError("Order")

    await session.delete(order)