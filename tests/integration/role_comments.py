import pytest
from src.schemas.roles import RoleCreate, RoleUpdate
from src.services.roles import (
    create_role,
    get_role,
    update_role,
    delete_role,
)
from src.exceptions.common import NotFoundError


@pytest.mark.asyncio
async def test_create_role(db_session):
    payload = RoleCreate(name="Admin")

    role = await create_role(db_session, payload)

    assert role.id is not None
    assert role.name == "Admin"


@pytest.mark.asyncio
async def test_get_role(db_session):
    role = await create_role(db_session, RoleCreate(name="Moderator"))

    fetched = await get_role(db_session, role.id)

    assert fetched.id == role.id
    assert fetched.name == "Moderator"


@pytest.mark.asyncio
async def test_update_role(db_session):
    role = await create_role(db_session, RoleCreate(name="User"))

    updated = await update_role(
        db_session,
        role.id,
        RoleUpdate(name="SuperUser")
    )

    assert updated.id == role.id
    assert updated.name == "SuperUser"


@pytest.mark.asyncio
async def test_delete_role(db_session):
    role = await create_role(db_session, RoleCreate(name="To be deleted"))

    # Удаляем
    await delete_role(db_session, role.id)

    # Проверяем, что теперь get вызывает NotFoundError
    with pytest.raises(NotFoundError):
        await get_role(db_session, role.id)
