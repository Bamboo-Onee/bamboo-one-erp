"""Configurações globais e fixtures para a suíte de testes com Pytest."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.core.database import engine


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def _dispose_db_pool_per_test():
    """Garante que conexões asyncpg do pool não fiquem presas a Event Loops encerrados entre testes."""
    await engine.dispose()
    yield
    await engine.dispose()


@pytest.fixture
async def async_client():
    """Fixture de cliente HTTP assíncrono para testes de integração com FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
