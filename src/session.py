from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from src.config.config import Settings

settings = Settings()

_engine = None
_sessionmaker = None


def get_engine():
    global _engine
    if _engine is None:
        settings = Settings()
        _engine = create_async_engine(
            str(settings.postgres_url),
            echo=False,
            future=True,
        )
    return _engine

def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
    )


async def get_async_session() -> AsyncSession:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
