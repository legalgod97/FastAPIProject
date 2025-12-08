from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.orders import OrderModel, NotificationModel

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
async def create_order_with_notification(data: dict, session: AsyncSession):
    order_data = data["order"]
    notif_data = data["notification"]

    order = OrderModel(
        id=order_data.get("id", uuid4()),
        total_amount=order_data["total_amount"],
        status=order_data["status"],
        payment_method=order_data["payment_method"],
        paid_at=order_data["paid_at"],
        user_id=order_data["user_id"]
    )

    notification = NotificationModel(
        id=uuid4(),
        message=notif_data["message"],
        type=notif_data["type"],
        is_read=notif_data["is_read"],
    )

    order.notification = notification

    session.add(order)
    await session.commit()

    return {"order_id": order.id, "notification_id": notification.id}

@router.get("/{order_id}")
async def get_order(order_id: UUID, session: AsyncSession):
    query = (
        select(OrderModel)
        .where(OrderModel.id == order_id)
        .options(selectinload(OrderModel.notification))
    )
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Order not found")

    return {
        "order": {
            "id": str(order.id),
            "total_amount": str(order.total_amount),
            "status": order.status.value,
            "payment_method": order.payment_method,
            "paid_at": order.paid_at.isoformat()
        },
        "notification": {
            "id": str(order.notification.id),
            "message": order.notification.message,
            "type": order.notification.type.value,
            "is_read": order.notification.is_read
        }
    }

@router.put("/{order_id}")
async def update_order(order_id: UUID, data: dict, session: AsyncSession):
    query = select(OrderModel).where(OrderModel.id == order_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Order not found")

    order_data = data["order"]
    notif_data = data["notification"]

    order.total_amount = order_data["total_amount"]
    order.status = order_data["status"]
    order.payment_method = order_data["payment_method"]
    order.paid_at = order_data["paid_at"]

    order.notification.message = notif_data["message"]
    order.notification.type = notif_data["type"]
    order.notification.is_read = notif_data["is_read"]

    await session.commit()
    return {"status": "updated"}

@router.delete("/{order_id}")
async def delete_order(order_id: UUID, session: AsyncSession):
    query = select(OrderModel).where(OrderModel.id == order_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Order not found")

    await session.delete(order)
    await session.commit()

    return {"status": "deleted"}