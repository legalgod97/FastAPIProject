import json
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.exceptions.common import NotFoundError
from src.schemas.posts import PostCreate, PostUpdate
from src.services.posts import (
    create_post,
    get_post,
    update_post,
    delete_post,
)
from src.models.posts import PostModel

@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def post_id():
    return uuid.uuid4()


@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.posts.PostRepository",
        MagicMock(return_value=repo),
    )

    return repo


@pytest.fixture
def mock_redis(monkeypatch):
    redis = AsyncMock()

    monkeypatch.setattr(
        "src.services.posts.redis",
        redis,
    )

    return redis


@pytest.fixture
def mock_post_model(monkeypatch):
    fake_model = MagicMock(spec=PostModel)
    fake_model.id = uuid.uuid4()
    fake_model.title = "hello"
    fake_model.content = "world"

    monkeypatch.setattr(
        "src.services.posts.PostModel",
        MagicMock(return_value=fake_model),
    )

    return fake_model


@pytest.mark.asyncio
async def test_create_post(
    session,
    mock_repo,
    mock_post_model,
):
    data = PostCreate(
        title="hello",
        content="world",
    )

    result = await create_post(session, data)

    mock_repo.create.assert_called_once_with(mock_post_model)
    assert result.title == "hello"
    assert result.content == "world"


@pytest.mark.asyncio
async def test_get_post_from_cache(
    session,
    post_id,
    mock_repo,
    mock_redis,
):
    cached = {
        "id": str(post_id),
        "title": "cached",
        "content": "post",
    }

    mock_redis.get.return_value = json.dumps(cached)

    result = await get_post(session, post_id)

    mock_repo.get_by_id.assert_not_called()
    assert result.title == "cached"


@pytest.mark.asyncio
async def test_get_post_from_db(
    session,
    post_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None

    post = MagicMock(spec=PostModel)
    post.id = post_id
    post.title = "db"
    post.content = "post"

    mock_repo.get_by_id.return_value = post

    result = await get_post(session, post_id)

    mock_repo.get_by_id.assert_called_once_with(post_id)
    mock_redis.set.assert_called_once()
    assert result.title == "db"


@pytest.mark.asyncio
async def test_get_post_not_found(
    session,
    post_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_post(session, post_id)


@pytest.mark.asyncio
async def test_update_post_success(
    session,
    post_id,
    mock_repo,
    mock_redis,
):
    post = MagicMock(spec=PostModel)
    post.id = post_id
    post.title = "old"
    post.content = "content"

    mock_repo.get_by_id.return_value = post

    data = PostUpdate(title="new")

    result = await update_post(session, post_id, data)

    assert post.title == "new"
    mock_redis.set.assert_called_once()
    assert result.title == "new"


@pytest.mark.asyncio
async def test_update_post_not_found(
    session,
    post_id,
    mock_repo,
):
    mock_repo.get_by_id.return_value = None

    data = PostUpdate(title="new")

    with pytest.raises(NotFoundError):
        await update_post(session, post_id, data)


@pytest.mark.asyncio
async def test_delete_post_success(
    session,
    post_id,
    mock_repo,
    mock_redis,
):
    mock_repo.get_by_id.return_value = MagicMock(spec=PostModel)

    await delete_post(session, post_id)

    mock_redis.delete.assert_called_once_with(f"post:{post_id}")
    mock_repo.delete_by_id.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_not_found(
    session,
    post_id,
    mock_repo,
):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await delete_post(session, post_id)
