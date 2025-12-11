from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.session import get_async_session
from models.roles import RoleModel
from schemas.roles import RoleCreate, RoleUpdate, RoleRead

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleRead)
async def create_role(
    data: RoleCreate,
    session: AsyncSession = Depends(get_async_session)
):
    role_data = data.model_dump(exclude_unset=True)
    role = RoleModel(**role_data)

    session.add(role)
    await session.commit()
    await session.refresh(role)

    return role


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    return role


# READ ALL
@router.get("/", response_model=list[RoleRead])
async def list_roles(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(RoleModel))
    return result.scalars().all()


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(role, key, value)

    await session.commit()
    await session.refresh(role)
    return role


@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    role = await session.get(RoleModel, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    await session.delete(role)
    await session.commit()

    return {"status": "deleted"}
