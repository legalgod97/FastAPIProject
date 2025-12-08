from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.users import UserModel
from src.models.orders import OrderModel

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user_with_orders(data: dict, session: AsyncSession):
    user_data = data["user"]
    orders_data = data.get("orders", [])

    user = UserModel(
        id=user_data.get("id", uuid4()),
        title=user_data["title"],
    )

    user_orders = []
    for order in orders_data:
        new_order = OrderModel(
            id=order.get("id", uuid4()),
            total_amount=order["total_amount"],
            status=order["status"],
            payment_method=order["payment_method"],
            paid_at=order["paid_at"],
        )
        user_orders.append(new_order)

    user.orders = user_orders

    session.add(user)
    await session.commit()

    return {
        "user": {
            "id": str(user.id),
            "title": user.title
        },
        "orders": [{"id": str(order.id)} for order in user.orders]
    }


@router.get("/{user_id}")
async def get_user(user_id: UUID, session: AsyncSession):
    query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.orders))
    user = (await session.execute(query)).scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "user": {
            "id": str(user.id),
            "title": user.title
        },
        "orders": [
            {
                "id": str(order.id),
                "total_amount": str(order.total_amount),
                "status": order.status.value,
                "payment_method": order.payment_method,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None
            }
            for order in user.orders
        ]
    }


@router.put("/{user_id}")
async def update_user(user_id: UUID, data: dict, session: AsyncSession):
    query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.orders))
    user = (await session.execute(query)).scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    user_data = data["user"]
    orders_data = data.get("orders", [])

    user.title = user_data["title"]
    user.orders.clear()

    for order in orders_data:
        user.orders.append(OrderModel(
            id=order.get("id", uuid4()),
            total_amount=order["total_amount"],
            status=order["status"],
            payment_method=order["payment_method"],
            paid_at=order["paid_at"],
        ))

    await session.commit()
    return {"status": "updated"}


@router.delete("/orders/{order_id}")
async def delete_order(order_id: UUID, session: AsyncSession):
    query = select(OrderModel).where(OrderModel.id == order_id)
    order = (await session.execute(query)).scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Order not found")

    await session.delete(order)
    await session.commit()

    return {"status": "deleted", "order_id": str(order_id)}


@router.delete("/{user_id}")
async def delete_user(user_id: UUID, session: AsyncSession):
    query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.orders))
    user = (await session.execute(query)).scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return {"status": "deleted", "user_id": str(user.id)}
