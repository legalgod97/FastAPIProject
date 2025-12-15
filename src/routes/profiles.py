from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.profiles import ProfileCreate, ProfileUpdate, ProfileRead
from services.profiles import (
    create_profile,
    get_profile,
    update_profile,
    delete_profile,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfileRead)
async def create_profile_route(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_async_session),
):
    profile = await create_profile(session, data)
    return profile


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile_route(
    profile_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    profile = await get_profile(session, profile_id)
    return profile


@router.put("/{profile_id}", response_model=ProfileRead)
async def update_profile_route(
    profile_id: UUID,
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    profile = await update_profile(session, profile_id, data)
    return profile


@router.delete("/{profile_id}")
async def delete_profile_route(
    profile_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_profile(session, profile_id)
    return {"status": "deleted"}
