from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from src.models.base import Base
from src.application.application import get_app
from src.session import get_async_session


@pytest.fixture
async def async_client(db_session):
    app = get_app()

    mock_producer = AsyncMock()
    mock_producer.publish.return_value = None
    app.state.kafka_producer = mock_producer

    app.dependency_overrides[get_async_session] = lambda: db_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14") as postgres:
        postgres.USER = "test"
        postgres.PASSWORD = "test"
        postgres.DBNAME = "test"

        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)

        async_url = f"postgresql+asyncpg://{postgres.USER}:{postgres.PASSWORD}@{host}:{port}/{postgres.DBNAME}"
        print("Postgres async URL:", async_url)
        yield async_url


@pytest.fixture
async def async_engine(postgres_container):
    engine = create_async_engine(
        postgres_container,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    async_session_maker = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = None
    mock.delete.return_value = None

    monkeypatch.setattr("src.services.roles.redis", mock)
    monkeypatch.setattr("src.services.posts.redis", mock)
    monkeypatch.setattr("src.services.users.redis", mock)


    return mock