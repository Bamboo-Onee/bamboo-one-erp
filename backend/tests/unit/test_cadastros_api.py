"""Testes de Integração dos Endpoints de Cadastros Mestres e Simulação 3D."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.core.database import init_db


@pytest.mark.asyncio
async def test_create_and_list_product():
    """Valida ciclo completo de criação e listagem de produto via API."""
    await init_db()
    unique_sku = f"BAM-TEST-{uuid.uuid4().hex[:6].upper()}"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "sku": unique_sku,
            "name": "Pallet Teste",
            "category": "Testes",
            "price": 250.0,
            "weight_kg": 45.0,
            "length_m": 1.2,
            "width_m": 1.0,
            "height_m": 1.4
        }
        res = await client.post("/api/v1/products", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["sku"] == unique_sku
        assert data["volume_m3"] == 1.68

        # Lista
        list_res = await client.get("/api/v1/products")
        assert list_res.status_code == 200
        items = list_res.json()
        assert any(i["sku"] == unique_sku for i in items)


@pytest.mark.asyncio
async def test_packing_simulation_endpoint():
    """Valida se a rota /pack-simulation devolve plano matemático tridimensional."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "truck_name": "Truck Baú Teste",
            "truck_length": 8.0,
            "truck_width": 2.4,
            "truck_height": 2.5,
            "truck_max_weight_kg": 12000.0,
            "items": [
                {"name": "Caixa A", "quantity": 2, "length_m": 1.0, "width_m": 1.0, "height_m": 1.0, "weight_kg": 100.0}
            ]
        }
        res = await client.post("/api/v1/logistics/pack-simulation", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "volumetric_efficiency_pct" in data
        assert "allocated_boxes" in data
        assert len(data["allocated_boxes"]) == 2
