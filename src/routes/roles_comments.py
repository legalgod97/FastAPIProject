from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.roles import RoleCreate, RoleUpdate, RoleRead
from services.roles import (
    create_role,
    get_role,
    update_role,
    delete_role,
)

router = APIRouter(
    prefix="/v1/roles_comments",
    tags=["v1", "roles_comments"],
)


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role_handler(
    data: RoleCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await create_role(session, data)


@router.get("/{role_id}", response_model=RoleRead, status_code=status.HTTP_200_OK)
async def get_role_handler(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await get_role(session, role_id)


@router.put("/{role_id}", response_model=RoleRead, status_code=status.HTTP_200_OK)
async def update_role_handler(
    role_id: UUID,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_role(session, role_id, data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_handler(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_role(session, role_id)

