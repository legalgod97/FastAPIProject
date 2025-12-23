from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from config.redis import redis, CACHE_TTL
from models.orders import OrderModel
from repositories.orders import OrderRepository
from schemas.orders import OrderCreate, OrderUpdate, OrderRead
from exceptions.common import NotFoundError
import logging

logger = logging.getLogger(__name__)


async def create_order(
    session: AsyncSession,
    data: OrderCreate,
) -> OrderRead:
    repo = OrderRepository(session)

    order = OrderModel(
        id=data.id or uuid4(),
        price=data.price,
    )

    await repo.create(order)

    return OrderRead.model_validate(order)


async def get_order(
    session: AsyncSession,
    order_id: UUID,
) -> OrderRead:
    cache_key = f"order:{order_id}"

    cached = await redis.get(cache_key)
    if cached:
        return OrderRead.model_validate_json(cached)

    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)

    if order is None:
        raise NotFoundError(f"Order with id {order_id} not found")

    data = OrderRead.model_validate(order)

    await redis.set(
        cache_key,
        data.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data


async def update_order(
    session: AsyncSession,
    order_id: UUID,
    data: OrderUpdate,
) -> OrderRead:
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)

    if order is None:
        message = f"Order with id {order_id} not found"
        logger.info(
            message,
            extra={"order_id": str(order_id)},
        )
        raise NotFoundError(message)

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(order, key, value)

    data_read = OrderRead.model_validate(order)

    await redis.set(
        f"order:{order_id}",
        data_read.model_dump_json(),
        ex=CACHE_TTL,
    )

    return data_read


async def delete_order(
    session: AsyncSession,
    order_id: UUID,
) -> None:
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)

    if order is None:
        message = f"Order with id {order_id} not found"
        logger.info(
            message,
            extra={"order_id": str(order_id)},
        )
        raise NotFoundError(message)

    await repo.delete(order)

    await redis.delete(f"order:{order_id}")