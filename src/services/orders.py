from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from models.orders import OrderModel
from schemas.orders import OrderCreate, OrderUpdate
from services.exceptions import NotFoundError


async def create_order(
    session: AsyncSession,
    data: OrderCreate,
) -> OrderModel:
    order: OrderModel = OrderModel(
        id=data.id or uuid4(),
        price=data.price,
    )

    session.add(order)
    await session.commit()
    await session.refresh(order)

    return order

async def get_order(
    session: AsyncSession,
    order_id: UUID,
) -> OrderModel:
    order: OrderModel | None = await session.get(OrderModel, order_id)

    if order is None:
        raise NotFoundError("Order")

    return order

async def update_order(
    session: AsyncSession,
    order_id: UUID,
    data: OrderUpdate,
) -> OrderModel:
    order: OrderModel | None = await session.get(OrderModel, order_id)

    if order is None:
        raise NotFoundError("Order")

    payload: dict = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(order, key, value)

    await session.commit()
    await session.refresh(order)

    return order

async def delete_order(
    session: AsyncSession,
    order_id: UUID,
) -> OrderModel:
    order: OrderModel | None = await session.get(OrderModel, order_id)

    if order is None:
        raise NotFoundError("Order")

    await session.delete(order)
    await session.commit()

    return order
