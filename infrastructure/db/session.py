from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.config import Settings

settings = Settings()

engine = create_engine(str(settings.postgres_url))


@contextmanager
async def get_session() -> Session:
    session: Session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()