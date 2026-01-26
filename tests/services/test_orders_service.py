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
def session():
    return MagicMock()


@pytest.fixture
def order_id():
    return uuid.uuid4()


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


@pytest.mark.asyncio
async def test_create_order(
    session,
    mock_repo,
    mock_order_model,
):
    data = OrderCreate(price=100)

    result = await create_order(session, data)

    mock_repo.create.assert_called_once_with(mock_order_model)
    assert result.price == 100


@pytest.mark.asyncio
async def test_get_order_from_cache(
    session,
    order_id,
    mock_repo,
    mock_redis,
):
    cached = {
        "id": str(order_id),
        "price": 200,
    }

    mock_redis.get.return_value = json.dumps(cached)

    result = await get_order(session, order_id)

    mock_repo.get_by_id.assert_not_called()
    assert result.price == 200


@pytest.mark.asyncio
async def test_get_order_from_db(
    session,
    order_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None

    order = MagicMock(spec=OrderModel)
    order.id = order_id
    order.price = 150
    order.post = None

    mock_repo.get_by_id.return_value = order

    result = await get_order(session, order_id)

    mock_repo.get_by_id.assert_called_once_with(order_id)
    mock_redis.set.assert_called_once()
    assert result.price == 150


@pytest.mark.asyncio
async def test_get_order_not_found(
    session,
    order_id,
    mock_repo,
    mock_redis,
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await get_order(session, order_id)


@pytest.mark.asyncio
async def test_update_order_success(
    session,
    order_id,
    mock_repo,
    mock_redis,
):
    order = MagicMock(spec=OrderModel)
    order.id = order_id
    order.price = 150
    order.post = None

    mock_repo.get_by_id.return_value = order

    data = OrderUpdate(price=300)

    result = await update_order(session, order_id, data)

    assert order.price == 300
    mock_redis.set.assert_called_once()
    assert result.price == 300


@pytest.mark.asyncio
async def test_update_order_not_found(
    session,
    order_id,
    mock_repo,
):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await update_order(session, order_id, OrderUpdate(price=200))


@pytest.mark.asyncio
async def test_delete_order_success(
    session,
    order_id,
    mock_repo,
    mock_redis,
):
    mock_repo.get_by_id.return_value = MagicMock(spec=OrderModel)

    await delete_order(session, order_id)

    mock_redis.delete.assert_called_once_with(f"order:{order_id}")
    mock_repo.delete_by_id.assert_called_once_with(order_id)


@pytest.mark.asyncio
async def test_delete_order_not_found(
    session,
    order_id,
    mock_repo,
):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await delete_order(session, order_id)
