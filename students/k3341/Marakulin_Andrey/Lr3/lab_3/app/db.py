from collections.abc import Generator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Session, create_engine

from .core.config import settings

try:
    engine = create_engine(settings.database_url, echo=False)
    async_engine = create_async_engine(settings.database_url, echo=False)
except ModuleNotFoundError:
    # Fallback for environments where PostgreSQL driver is not installed yet.
    engine = create_engine("sqlite:///./personal_finance_lab1.db", echo=False)
    async_engine = create_async_engine("sqlite+aiosqlite:///./personal_finance_lab1.db", echo=False)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
