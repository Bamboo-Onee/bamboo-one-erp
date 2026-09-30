"""Infraestrutura de Banco de Dados Assíncrono com SQLAlchemy 2.0.

Suporta PostgreSQL com fallback gracioso para SQLite local assíncrono (aiosqlite)
para garantir persistência real imediata mesmo em ambientes de desenvolvimento offline.
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.config.settings import settings

# Determina URL de conexão assíncrona (Postgres ou SQLite local)
DATABASE_URL = settings.DATABASE_URL
if "postgres" in DATABASE_URL and os.environ.get("USE_SQLITE", "true").lower() == "true":
    DATABASE_URL = "sqlite+aiosqlite:///./crm_bamboo.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
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
