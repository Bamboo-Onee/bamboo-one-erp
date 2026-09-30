"""Configurações globais e fixtures para a suíte de testes com Pytest."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    """Fixture de cliente HTTP assíncrono para testes de integração com FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
