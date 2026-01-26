import json
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.exceptions.common import NotFoundError
from src.schemas.profiles import ProfileCreate, ProfileUpdate
from src.services.profiles import (
    create_profile,
    get_profile,
    update_profile,
    delete_profile,
)
from src.models.profiles import ProfileModel


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def profile_id():
    return uuid.uuid4()


@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.profiles.ProfileRepository",
        MagicMock(return_value=repo),
    )

    return repo


@pytest.fixture
def mock_redis(monkeypatch):
    redis = AsyncMock()

    monkeypatch.setattr(
        "src.services.profiles.redis",
        redis,
    )

    return redis


@pytest.fixture
def mock_profile_model(monkeypatch):
    def factory(**kwargs):
        obj = MagicMock()

        obj.id = kwargs.get("id")
        obj.full_name = kwargs.get("full_name")
        obj.bio = kwargs.get("bio")
        obj.owner_id = kwargs.get("owner_id")
        obj.role_id = None
        obj.role_o2m_id = None

        return obj

    mock_cls = MagicMock(side_effect=factory)

    monkeypatch.setattr(
        "src.services.profiles.ProfileModel",
        mock_cls,
    )

    return mock_cls



@pytest.mark.asyncio
async def test_create_profile(
    session,
    mock_repo,
    mock_profile_model,
):
    owner_id = uuid.uuid4()

    data = ProfileCreate(
        full_name="John Doe",
        bio="Bio",
    )

    result = await create_profile(
        session=session,
        owner_id=owner_id,
        data=data,
    )

    mock_repo.create.assert_awaited_once()

    args, _ = mock_repo.create.await_args
    created_profile = args[0]

    assert created_profile.owner_id == owner_id
    assert created_profile.full_name == "John Doe"
    assert created_profile.bio == "Bio"




@pytest.mark.asyncio
async def test_get_profile_from_cache(
    session,
    profile_id,
    mock_repo,
    mock_redis,
):
    cached = {
        "id": str(profile_id),
        "full_name": "Cached User",
        "bio": "Cached bio",
        "owner_id": str(uuid.uuid4()),
    }

    mock_redis.get.return_value = json.dumps(cached)

    result = await get_profile(session, profile_id)

    mock_repo.get_by_id.assert_not_called()
    assert result.full_name == "Cached User"


@pytest.mark.asyncio
async def test_get_profile_from_db(
    session,
    profile_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None

    profile = MagicMock(spec=ProfileModel)
    profile.id = profile_id
    profile.full_name = "DB User"
    profile.bio = "DB bio"
    profile.owner_id = uuid.uuid4()

    mock_repo.get_by_id.return_value = profile

    result = await get_profile(session, profile_id)

    mock_repo.get_by_id.assert_called_once_with(profile_id)
    mock_redis.set.assert_called_once()
    assert result.full_name == "DB User"


@pytest.mark.asyncio
async def test_get_profile_not_found(
    session,
    profile_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_profile(session, profile_id)


@pytest.mark.asyncio
async def test_update_profile_success(
    session,
    profile_id,
    mock_repo,
    mock_redis,
):
    profile = MagicMock(spec=ProfileModel)
    profile.id = profile_id
    profile.full_name = "Old Name"
    profile.bio = "Old bio"
    profile.owner_id = uuid.uuid4()

    mock_repo.get_by_id.return_value = profile

    data = ProfileUpdate(
        full_name="New Name",
        bio="New bio",
    )

    result = await update_profile(session, profile_id, data)

    assert profile.full_name == "New Name"
    assert profile.bio == "New bio"
    mock_redis.set.assert_called_once()
    assert result.full_name == "New Name"


@pytest.mark.asyncio
async def test_delete_profile_success(
    session,
    profile_id,
    mock_repo,
    mock_redis,
):
    mock_repo.get_by_id.return_value = MagicMock(spec=ProfileModel)

    await delete_profile(session, profile_id)

    mock_redis.delete.assert_called_once_with(f"profile:{profile_id}")
    mock_repo.delete_by_id.assert_called_once_with(profile_id)
