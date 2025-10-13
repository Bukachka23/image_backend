import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseConnection:
    """Manages database connection and sessions"""

    def __init__(self, database_url: str):
        self.database_url = database_url

        self.is_async = database_url.startswith("postgresql+asyncpg") or database_url.startswith("sqlite+aiosqlite")

        if self.is_async:
            self.engine = create_async_engine(database_url, echo=False, future=True)
            self.SessionFactory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        else:
            connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
            self.engine = create_engine(
                database_url,
                connect_args=connect_args,
                echo=False
            )
            self.SessionFactory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

    async def create_tables(self):
        """Create all tables"""
        from src.infrastructure.database.models import Base

        if self.is_async:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            Base.metadata.create_all(bind=self.engine)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        """Get a database session"""
        if self.is_async:
            async with self.SessionFactory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        else:
            session = self.SessionFactory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()


_db_connection: DatabaseConnection | None = None


def initialize_database(database_url: str = None) -> DatabaseConnection:
    """Initialize database connection"""
    global _db_connection

    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./credits.db")

    _db_connection = DatabaseConnection(database_url)
    return _db_connection


def get_database() -> DatabaseConnection:
    """Get the database connection instance"""
    global _db_connection
    if _db_connection is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _db_connection
