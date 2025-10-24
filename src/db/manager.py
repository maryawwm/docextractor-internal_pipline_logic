import contextlib
from typing import Any, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.settings import app_settings


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] | None = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_engine(host, **engine_kwargs)
        self._sessionmaker = sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False
        )

    def close(self) -> None:
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


sessionmanager = DatabaseSessionManager(app_settings.database_url)


def get_db_session() -> Iterator[Session]:
    with sessionmanager.session() as session:
        yield session
