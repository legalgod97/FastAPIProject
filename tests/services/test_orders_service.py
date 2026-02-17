import json
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.exceptions.common import NotFoundError
from src.schemas.orders import OrderCreate, OrderUpdate
from src.services.orders import (
    create_order,
    get_order,
    update_order,
    delete_order,
)
from src.models.orders import OrderModel


@pytest.fixture
def mock_repo(monkeypatch):
    repo = AsyncMock()

    monkeypatch.setattr(
        "src.services.orders.OrderRepository",
        MagicMock(return_value=repo),
    )

    return repo


@pytest.fixture
def mock_redis(monkeypatch):
    redis = AsyncMock()

    monkeypatch.setattr(
        "src.services.orders.redis",
        redis,
    )

    return redis


@pytest.fixture
def mock_order_model(monkeypatch):
    fake_model = MagicMock(spec=OrderModel)
    fake_model.id = uuid.uuid4()
    fake_model.price = 100

    monkeypatch.setattr(
        "src.services.orders.OrderModel",
        MagicMock(return_value=fake_model),
    )

    return fake_model

@pytest.fixture
def mock_order(id) -> OrderModel:
    order = MagicMock(spec=OrderModel)
    order.id = id
    order.price = 150
    order.post = None
    return order


@pytest.mark.asyncio
async def test_create_order(session, mock_repo, mock_order):
    data = OrderCreate(price=mock_order.price)

    mock_repo.create.return_value = mock_order

    result = await create_order(session, data)

    mock_repo.create.assert_called_once()
    created_order = mock_repo.create.call_args[0][0]
    assert created_order.price == mock_order.price


@pytest.mark.asyncio
async def test_get_order_from_cache(session, id, mock_repo, mock_redis, mock_order):
    cached = {
        "id": str(id),
        "price": mock_order.price,
        "post": mock_order.post,
    }

    mock_redis.get.return_value = json.dumps(cached)

    result = await get_order(session, id)

    mock_repo.get_by_id.assert_not_called()
    mock_redis.get.assert_awaited_once_with(f"order:{id}")
    assert result.price == mock_order.price


@pytest.mark.asyncio
async def test_get_order_from_db(session, id, mock_repo, mock_redis, mock_order):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = mock_order

    result = await get_order(session, id)

    mock_repo.get_by_id.assert_called_once_with(id)
    mock_redis.set.assert_called_once()
    assert result.price == mock_order.price


@pytest.mark.asyncio
async def test_get_order_not_found(session, id, mock_repo, mock_redis):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_order(session, id)


@pytest.mark.asyncio
async def test_update_order_success(session, id, mock_repo, mock_redis, mock_order):
    mock_repo.get_by_id.return_value = mock_order
    data = OrderUpdate(price=300)

    result = await update_order(session, id, data)

    assert mock_order.price == 300
    mock_redis.set.assert_called_once()
    assert result.price == 300


@pytest.mark.asyncio
async def test_update_order_not_found(session, id, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await update_order(session, id, OrderUpdate(price=200))


@pytest.mark.asyncio
async def test_delete_order_success(session, id, mock_repo, mock_redis, mock_order):
    mock_repo.get_by_id.return_value = mock_order

    await delete_order(session, id)

    mock_redis.delete.assert_called_once_with(f"order:{id}")
    mock_repo.delete_by_id.assert_called_once_with(id)


@pytest.mark.asyncio
async def test_delete_order_not_found(session, id, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await delete_order(session, id)