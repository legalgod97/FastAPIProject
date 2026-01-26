import pytest
from unittest.mock import AsyncMock, MagicMock

from uuid import uuid4

from src.services.users import (
    create_user,
    get_user,
    update_user,
)
from src.schemas.users import UserCreate, UserUpdate
from src.schemas.profiles import ProfileCreate
from src.exceptions.common import NotFoundError


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def producer():
    producer = AsyncMock()
    producer.publish.return_value = None
    return producer


@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.users.UserRepository",
        MagicMock(return_value=repo),
    )

    return repo


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = None
    redis_mock.delete.return_value = None

    monkeypatch.setattr("src.services.users.redis", redis_mock)
    return redis_mock


@pytest.fixture
def mock_user_model(monkeypatch):
    def factory(**kwargs):
        obj = MagicMock()
        obj.id = kwargs.get("id", uuid4())
        obj.name = kwargs.get("name")
        obj.profile = None
        return obj

    mock_cls = MagicMock(side_effect=factory)

    monkeypatch.setattr(
        "src.services.users.UserModel",
        mock_cls,
    )

    return mock_cls


@pytest.fixture
def mock_profile_model(monkeypatch):
    mock_cls = MagicMock()

    monkeypatch.setattr(
        "src.services.users.ProfileModel",
        mock_cls,
    )

    return mock_cls


@pytest.mark.asyncio
async def test_create_user(
    session,
    producer,
    mock_repo,
    mock_user_model,
):
    data = UserCreate(
        name="John",
    )

    result = await create_user(
        session=session,
        data=data,
        producer=producer,
    )

    mock_repo.create.assert_awaited_once()
    producer.publish.assert_awaited_once()

    assert result.id is not None
    assert result.name == "John"


@pytest.mark.asyncio
async def test_get_user(
    session,
    mock_repo,
):
    user_id = uuid4()

    user = MagicMock()
    user.id = user_id
    user.name = "John"

    mock_repo.get_by_id.return_value = user

    result = await get_user(
        session=session,
        user_id=user_id,
    )

    mock_repo.get_by_id.assert_awaited_once_with(user_id)
    assert result.id == user_id
    assert result.name == "John"


@pytest.mark.asyncio
async def test_get_user_not_found(
    session,
    mock_repo,
):
    user_id = uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_user(
            session=session,
            user_id=user_id,
        )


@pytest.mark.asyncio
async def test_update_user(
    session,
    producer,
    mock_repo,
):
    user_id = uuid4()

    user = MagicMock()
    user.id = user_id
    user.name = "Old name"
    user.profile = None

    mock_repo.get_by_id.return_value = user

    data = UserUpdate(
        name="New name",
    )

    result = await update_user(
        session=session,
        user_id=user_id,
        data=data,
        producer=producer,
    )

    assert user.name == "New name"
    producer.publish.assert_awaited_once()
    assert result.name == "New name"


@pytest.mark.asyncio
async def test_update_user_with_profile(
    session,
    producer,
    mock_repo,
    mock_profile_model,
):
    user_id = uuid4()

    user = MagicMock()
    user.id = user_id
    user.name = "John"
    user.profile = None

    mock_repo.get_by_id.return_value = user

    data = UserUpdate(
        name="John Updated",
    )

    profile_data = ProfileCreate(
        full_name="John Doe",
        bio="Bio",
    )

    result = await update_user(
        session=session,
        user_id=user_id,
        data=data,
        producer=producer,
        profile_data=profile_data,
    )

    mock_profile_model.assert_called_once()
    assert user.profi
