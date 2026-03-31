from collections.abc import Generator

from sqlmodel import Session, create_engine

from .core.config import settings

try:
    engine = create_engine(settings.database_url, echo=False)
except ModuleNotFoundError:
    # Fallback for environments where PostgreSQL driver is not installed yet.
    engine = create_engine("sqlite:///./personal_finance_lab1.db", echo=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
