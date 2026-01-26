import json
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock
from src.exceptions.common import NotFoundError
from src.schemas.comments import CommentCreate, CommentUpdate
from src.services.comments import (
    create_comment,
    get_comment,
    update_comment,
    delete_comment,
)
from src.models.comments import CommentModel


@pytest.fixture
def session():
    return MagicMock()

@pytest.fixture
def comment_id():
    return uuid.uuid4()

@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.comments.CommentRepository",
        MagicMock(return_value=repo),
    )

    return repo

@pytest.fixture
def mock_redis(monkeypatch):
    redis = AsyncMock()

    monkeypatch.setattr(
        "src.services.comments.redis",
        redis,
    )

    return redis

@pytest.fixture
def mock_comment_model(monkeypatch):
    fake_model = MagicMock()
    fake_model.id = uuid.uuid4()
    fake_model.content = "hello"
    fake_model.is_edited = False
    fake_model.role = None

    monkeypatch.setattr(
        "src.services.comments.CommentModel",
        MagicMock(return_value=fake_model),
    )

    return fake_model

@pytest.mark.asyncio
async def test_create_comment(
    session,
    mock_repo,
    mock_comment_model,
):
    data = CommentCreate(
        content="hello",
        post_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        role_id=uuid.uuid4(),
    )

    result = await create_comment(session, data)

    mock_repo.create.assert_called_once_with(mock_comment_model)
    assert result.content == "hello"


@pytest.mark.asyncio
async def test_get_comment_from_cache(
    session,
    comment_id,
    mock_repo,
    mock_redis,
):
    cached = {
        "id": str(comment_id),
        "content": "cached",
        "is_edited": False,
        "role": None,
    }

    mock_redis.get.return_value = json.dumps(cached)

    result = await get_comment(session, comment_id)

    mock_repo.get_by_id.assert_not_called()
    assert result.content == "cached"


@pytest.mark.asyncio
async def test_get_comment_from_db(
    session,
    comment_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None

    comment = MagicMock(spec=CommentModel)
    comment.id = comment_id
    comment.content = "db"
    comment.is_edited = False
    comment.role = None

    mock_repo.get_by_id.return_value = comment

    result = await get_comment(session, comment_id)

    mock_repo.get_by_id.assert_called_once_with(comment_id)
    mock_redis.set.assert_called_once()
    assert result.content == "db"


@pytest.mark.asyncio
async def test_get_comment_not_found(
    session,
    comment_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_comment(session, comment_id)


@pytest.mark.asyncio
async def test_update_comment_success(
    session,
    comment_id,
    mock_repo,
    mock_redis,
):
    comment = MagicMock(spec=CommentModel)
    comment.id = comment_id
    comment.content = "old"
    comment.is_edited = False
    comment.role = None

    mock_repo.get_by_id.return_value = comment

    data = CommentUpdate(content="new")

    result = await update_comment(session, comment_id, data)

    assert comment.content == "new"
    assert comment.is_edited is True
    mock_redis.set.assert_called_once()
    assert result.content == "new"


@pytest.mark.asyncio
async def test_delete_comment_success(
    session,
    comment_id,
    mock_repo,
    mock_redis,
):
    mock_repo.get_by_id.return_value = MagicMock(spec=CommentModel)

    await delete_comment(session, comment_id)

    mock_redis.delete.assert_called_once_with(f"comment:{comment_id}")
    mock_repo.delete_by_id.assert_called_once_with(comment_id)


