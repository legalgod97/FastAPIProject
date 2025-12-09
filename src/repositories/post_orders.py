from fastapi import APIRouter, HTTPException
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.orders import OrderModel
from models.posts import PostModel, post_order

router = APIRouter(prefix="/posts", tags=["post_orders"])


@router.post("/")
async def create_post_order(data: dict, session: AsyncSession):
    post_id = UUID(data["post_id"])
    order_data = data["order"]

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    order_id = UUID(order_data.get("id", uuid4()))
    order = (await session.execute(
        select(OrderModel).where(OrderModel.id == order_id)
    )).scalar_one_or_none()
    if not order:
        order = OrderModel(
            id=order_id,
            total_amount=order_data["total_amount"],
            status=order_data["status"],
            payment_method=order_data["payment_method"],
            paid_at=order_data["paid_at"],
            user_id=order_data["user_id"]
        )
        session.add(order)
        await session.commit()

    existing = (await session.execute(
        select(post_order).where(
            and_(
                post_order.c.post_id == post_id,
                post_order.c.order_id == order.id
            )
        )
    )).first()
    if existing:
        raise HTTPException(400, "Relation already exists")

    await session.execute(
        post_order.insert().values(
            post_id=post_id,
            order_id=order.id
        )
    )
    await session.commit()

    return {"status": "created", "post_id": str(post_id), "order_id": str(order.id)}


@router.get("/{post_id}/orders")
async def get_post_orders(post_id: UUID, session: AsyncSession):
    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    rows = (await session.execute(
        select(post_order.c.order_id).where(
            and_(post_order.c.post_id == post_id)
        )
    )).scalars().all()

    orders = []
    for o_id in rows:
        order = (await session.execute(
            select(OrderModel).where(OrderModel.id == o_id)
        )).scalar_one()
        orders.append({
            "id": str(order.id),
            "total_amount": str(order.total_amount),
            "status": order.status.value,
            "payment_method": order.payment_method,
            "paid_at": order.paid_at.isoformat()
        })

    return {"post_id": str(post_id), "orders": orders}


@router.put("/")
async def update_post_order(data: dict, session: AsyncSession):
    post_id = UUID(data["post_id"])
    order_data = data["order"]
    order_id = UUID(order_data["id"])

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    order = (await session.execute(
        select(OrderModel).where(OrderModel.id == order_id)
    )).scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    order.total_amount = order_data["total_amount"]
    order.status = order_data["status"]
    order.payment_method = order_data["payment_method"]
    order.paid_at = order_data["paid_at"]

    existing_link = (await session.execute(
        select(post_order).where(
            and_(
                post_order.c.post_id == post_id,
                post_order.c.order_id == order_id
            )
        )
    )).first()
    if not existing_link:

        await session.execute(
            post_order.insert().values(
                post_id=post_id,
                order_id=order_id
            )
        )

    await session.commit()
    return {"status": "updated", "post_id": str(post_id), "order_id": str(order_id)}


@router.delete("/")
async def delete_post_order(data: dict, session: AsyncSession):
    post_id = UUID(data["post_id"])
    order_id = UUID(data["order_id"])

    existing = (await session.execute(
        select(post_order).where(
            and_(
                post_order.c.post_id == post_id,
                post_order.c.order_id == order_id
            )
        )
    )).first()
    if not existing:
        raise HTTPException(404, "Relation not found")

    await session.execute(
        post_order.delete().where(
            and_(
                post_order.c.post_id == post_id,
                post_order.c.order_id == order_id
            )
        )
    )
    await session.commit()

    return {"status": "deleted", "post_id": str(post_id), "order_id": str(order_id)}
