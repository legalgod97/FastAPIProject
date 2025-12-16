from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_async_session
from schemas.common import DeleteResult
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


@router.post("/", response_model=RoleRead)
async def create_role_route(
    data: RoleCreate,
    session: AsyncSession = Depends(get_async_session),
):
    role = await create_role(session, data)
    return role


@router.get("/{role_id}", response_model=RoleRead)
async def get_role_route(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    role = await get_role(session, role_id)
    return role


@router.put("/{role_id}", response_model=RoleRead)
async def update_role_route(
    role_id: UUID,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    role = await update_role(session, role_id, data)
    return role


@router.delete("/{role_id}", response_model=DeleteResult)
async def delete_role_route(
    role_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    await delete_role(session, role_id)
    return DeleteResult(status="deleted")
