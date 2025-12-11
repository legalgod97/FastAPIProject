from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from models.orders import OrderModel
from schemas.orders import OrderCreate, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_async_session)
):
    order = OrderModel(
        id=data.id or uuid4(),
        price=data.price,
    )

    session.add(order)
    await session.commit()

    return {"id": str(order.id)}


@router.get("/{order_id}")
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    return {
        "id": str(order.id),
        "price": order.price,
    }


@router.put("/{order_id}")
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    if data.price is not None:
        order.price = data.price

    await session.commit()
    return {"status": "updated"}


@router.delete("/{order_id}")
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    await session.delete(order)
    await session.commit()

    return {"status": "deleted"}
