"""Infraestrutura de Banco de Dados Assíncrono com SQLAlchemy 2.0.

Suporta PostgreSQL com fallback gracioso para SQLite local assíncrono (aiosqlite)
para garantir persistência real imediata mesmo em ambientes de desenvolvimento offline.
"""

import os
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.config.settings import settings

# Determina URL de conexão assíncrona (Postgres ou SQLite local)
DATABASE_URL = settings.DATABASE_URL
if os.environ.get("USE_SQLITE", "true").lower() == "true" or "sqlite" in DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./crm_bamboo.db"
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"timeout": 30},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        """Habilita modo WAL e busy_timeout no SQLite para leituras/escritas paralelas."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        cursor.close()
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,
    )

async_session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(DeclarativeBase):
    """Classe base declarativa compartilhada para todos os modelos ORM."""
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection de sessão do banco para roteadores FastAPI."""
    async with async_session_factory() as session:
        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Cria todas as tabelas registradas no metadata caso ainda não existam."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
