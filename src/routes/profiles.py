# profiles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.session import get_async_session
from models.profiles import ProfileModel
from schemas.profiles import ProfileCreate, ProfileUpdate, ProfileRead

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfileRead)
async def create_profile(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_async_session)
):
    # use model_dump instead of dict()
    profile_data = data.model_dump(exclude_unset=True)
    profile = ProfileModel(**profile_data)
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    profile = await session.get(ProfileModel, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile


@router.get("/", response_model=list[ProfileRead])
async def list_profiles(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(ProfileModel))
    return result.scalars().all()


@router.put("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    profile = await session.get(ProfileModel, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(profile, k, v)

    await session.commit()
    await session.refresh(profile)
    return profile


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    profile = await session.get(ProfileModel, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    await session.delete(profile)
    await session.commit()

    return {"status": "deleted"}
