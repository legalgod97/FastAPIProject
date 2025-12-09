from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infrastructure.db.models.profiles import ProfileModel
from infrastructure.db.models.users import UserModel
from infrastructure.db.models.orders import OrderModel

router = APIRouter(prefix="/users", tags=["users"])
orders_router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
async def create_user_with_profile(data: dict, session: AsyncSession):
    user_data = data["user"]
    profile_data = data["profile"]

    user = UserModel(
        id=user_data.get("id", uuid4()),
        title=user_data["title"],
    )

    profile = ProfileModel(
        id=profile_data.get("id", uuid4()),
        full_name=profile_data["full_name"],
        avatar_url=profile_data["avatar_url"],
        bio=profile_data["bio"],
        location=profile_data["location"],
        birth_date=profile_data["birth_date"],
        gender=profile_data["gender"],
        phone_number=profile_data["phone_number"],
    )

    user.profile = profile

    session.add(user)
    await session.commit()

    return {"user_id": str(user.id), "profile_id": str(profile.id)}


@router.get("/{user_id}")
async def get_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.profile))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    profile = user.profile
    return {
        "user": {
            "id": str(user.id),
            "title": user.title,
        },
        "profile": {
            "id": str(profile.id),
            "full_name": profile.full_name,
            "avatar_url": profile.avatar_url,
            "bio": profile.bio,
            "location": profile.location,
            "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
            "gender": profile.gender,
            "phone_number": profile.phone_number,
        }
    }


@router.put("/{user_id}")
async def update_user(user_id: UUID, data: dict, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.profile))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")
    if not user.profile:
        raise HTTPException(500, "Profile missing for this user")

    user_data = data["user"]
    profile_data = data["profile"]

    user.title = user_data["title"]
    user.profile.full_name = profile_data["full_name"]
    user.profile.avatar_url = profile_data["avatar_url"]
    user.profile.bio = profile_data["bio"]
    user.profile.location = profile_data["location"]
    user.profile.birth_date = (
        datetime.fromisoformat(profile_data["birth_date"])
        if profile_data.get("birth_date") else None
    )
    user.profile.gender = profile_data["gender"]
    user.profile.phone_number = profile_data["phone_number"]

    await session.commit()
    return {"status": "updated"}


@router.delete("/{user_id}")
async def delete_user(user_id: UUID, session: AsyncSession):
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.profile))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return {"status": "deleted"}


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
