from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infrastructure.db.models.roles import RoleModel
from infrastructure.db.models.users import UserModel
from infrastructure.db.models.orders import OrderModel

router = APIRouter(prefix="/users", tags=["users"])
orders_router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
async def create_user_with_role(data: dict, session: AsyncSession):
    user_data = data["user"]
    role_data = data["role"]

    user = UserModel(
        id=user_data.get("id", uuid4()),
        title=user_data["title"],
    )

    role = RoleModel(
        name=role_data["name"],
        description=role_data.get("description"),
    )

    user.role = role

    session.add(user)
    await session.commit()

    return {"user_id": str(user.id), "role_name": role.name}


@router.get("/{user_id}")
async def get_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.role))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    role = user.role
    return {
        "user": {
            "id": str(user.id),
            "title": user.title,
        },
        "role": {
            "name": role.name,
            "description": role.description,
        }
    }


@router.put("/{user_id}")
async def update_user(user_id: UUID, data: dict, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.role))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")
    if not user.role:
        raise HTTPException(500, "Role missing for this user")

    user_data = data["user"]
    role_data = data["role"]

    user.title = user_data["title"]
    user.role.name = role_data["name"]
    user.role.description = role_data.get("description")

    await session.commit()
    return {"status": "updated"}


@orders_router.delete("/{order_id}")
async def delete_order(order_id: UUID, session: AsyncSession):
    query = select(OrderModel).where(OrderModel.id == order_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Order not found")

    await session.delete(order)
    await session.commit()

    return {"status": "deleted", "order_id": str(order_id)}


@router.delete("/{user_id}")
async def delete_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.role))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return {"status": "deleted"}
