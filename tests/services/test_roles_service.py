import uuid

from unittest.mock import AsyncMock, MagicMock

from src.schemas.comments import CommentCreate

import pytest
from uuid import uuid4

from src.services.roles import create_role, update_role, delete_role
from src.schemas.roles import RoleCreate, RoleUpdate


@pytest.fixture
def session():
    return MagicMock()

@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.roles.RoleRepository",
        MagicMock(return_value=repo),
    )

    return repo


@pytest.fixture
def mock_role_model(monkeypatch):
    def factory(**kwargs):
        obj = MagicMock()

        obj.id = kwargs.get("id", uuid4())
        obj.name = kwargs.get("name")
        obj.description = kwargs.get("description")
        obj.main_comment = kwargs.get("main_comment")

        return obj

    mock_cls = MagicMock(side_effect=factory)

    monkeypatch.setattr(
        "src.services.roles.RoleModel",
        mock_cls,
    )

    return mock_cls


@pytest.fixture
def mock_comment_model(monkeypatch):
    mock_cls = MagicMock()

    monkeypatch.setattr(
        "src.services.roles.CommentModel",
        mock_cls,
    )

    return mock_cls

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = None
    redis_mock.delete.return_value = None

    monkeypatch.setattr("src.services.roles.redis", redis_mock)
    return redis_mock


@pytest.mark.asyncio
async def test_create_role(
    session,
    mock_repo,
    mock_role_model,
):
    data = RoleCreate(
        name="Admin",
        description="Administrator role",
    )

    result = await create_role(
        session=session,
        data=data,
    )

    mock_repo.create.assert_awaited_once()
    assert result.name == "Admin"
    assert result.description == "Administrator role"


from src.services.roles import get_role


@pytest.mark.asyncio
async def test_get_role(
    session,
    mock_repo,
):
    role_id = uuid4()

    role = MagicMock()
    role.id = role_id
    role.name = "Admin"
    role.description = "Administrator role"
    role.main_comment = None

    mock_repo.get_by_id.return_value = role

    result = await get_role(
        session=session,
        role_id=role_id,
    )

    mock_repo.get_by_id.assert_awaited_once_with(role_id)
    assert result.id == role_id


import pytest
from src.exceptions.common import NotFoundError


@pytest.mark.asyncio
async def test_get_role_not_found(
    session,
    mock_repo,
):
    role_id = uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_role(
            session=session,
            role_id=role_id,
        )


@pytest.mark.asyncio
async def test_update_role(
    session,
    mock_repo,
):
    role_id = uuid4()

    role = MagicMock()
    role.id = role_id
    role.name = "Old"
    role.description = "Old desc"
    role.main_comment = None

    mock_repo.get_by_id.return_value = role

    data = RoleUpdate(
        name="New",
    )

    result = await update_role(
        session=session,
        role_id=role_id,
        data=data,
    )

    assert role.name == "New"
    assert result.name == "New"

@pytest.mark.asyncio
async def test_update_role_with_comment(
    session,
    mock_repo,
    mock_comment_model,
):
    role_id = uuid4()

    role = MagicMock()
    role.id = role_id
    role.name = "Admin"
    role.description = "Admin role"
    role.main_comment = None

    mock_repo.get_by_id.return_value = role

    role_data = RoleUpdate(
        description="Updated",
    )

    comment_data = CommentCreate(
        content="Main comment",
        post_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        role_id=role_id,
    )

    result = await update_role(
        session=session,
        role_id=role_id,
        data=role_data,
        comment_data=comment_data,
    )

    mock_comment_model.assert_called_once()
    assert role.main_comment is not None

@pytest.mark.asyncio
async def test_delete_role_not_found(
    session,
    mock_repo,
):
    role_id = uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await delete_role(
            session=session,
            role_id=role_id,
        )