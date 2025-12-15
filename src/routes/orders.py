from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.orders import OrderCreate, OrderUpdate
from services.orders import (
    create_order,
    get_order,
    update_order,
    delete_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
async def create_order_route(
    data: OrderCreate,
    session: AsyncSession = Depends(get_async_session),
):
    order = await create_order(session, data)
    return {
        "id": str(order.id),
        "price": order.price,
    }


@router.get("/{order_id}")
async def get_order_route(
    order_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    order = await get_order(session, order_id)
    return {
        "id": str(order.id),
        "price": order.price,
    }


@router.put("/{order_id}")
async def update_order_route(
    order_id: UUID,
    data: OrderUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    order = await update_order(session, order_id, data)
    return {
        "id": str(order.id),
        "price": order.price,
    }


@router.delete("/{order_id}")
async def delete_order_route(
    order_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_order(session, order_id)
    return {"status": "deleted"}
