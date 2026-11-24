"""Testes de Integração dos Endpoints de Cadastros Mestres, RBAC e Simulação 3D (Casos Positivos e Negativos)."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app, seed_initial_data
from src.core.database import init_db
from src.core.security import create_access_token


def _auth_header(email: str, role: str) -> dict[str, str]:
    token = create_access_token({"sub": email, "name": role.title(), "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_list_and_delete_product_with_rbac():
    """Valida criação, listagem, bloqueio de acesso anônimo (401) e restrição de exclusão a ADMIN (403 vs 204)."""
    await init_db()
    await seed_initial_data()

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

        # 1. [CASO NEGATIVO - NÃO PASSA] Criação sem token JWT -> 401 Unauthorized
        res_unauth = await client.post("/api/v1/products", json=payload)
        assert res_unauth.status_code == 401

        # 2. [CASO POSITIVO - PASSA] Criação autenticada com papel VENDAS -> 201 Created
        vendas_headers = _auth_header("vendas@bamboo.com", "VENDAS")
        res = await client.post("/api/v1/products", headers=vendas_headers, json=payload)
        assert res.status_code == 201
        data = res.json()
        product_id = data["id"]
        assert data["sku"] == unique_sku
        assert data["volume_m3"] == 1.68

        # 3. [CASO NEGATIVO - NÃO PASSA] SKU duplicado -> 400 Bad Request
        res_dup = await client.post("/api/v1/products", headers=vendas_headers, json=payload)
        assert res_dup.status_code == 400

        # 4. [CASO POSITIVO - PASSA] Listagem autenticada -> 200 OK
        list_res = await client.get("/api/v1/products", headers=vendas_headers)
        assert list_res.status_code == 200
        items = list_res.json()
        assert any(i["sku"] == unique_sku for i in items)

        # 5. [CASO NEGATIVO - NÃO PASSA] Usuário VENDAS tentando excluir produto -> 403 Forbidden
        del_forbidden = await client.delete(f"/api/v1/products/{product_id}", headers=vendas_headers)
        assert del_forbidden.status_code == 403

        # 6. [CASO POSITIVO - PASSA] Usuário ADMIN excluindo produto -> 204 No Content
        admin_headers = _auth_header("admin@bamboo.com", "ADMIN")
        del_ok = await client.delete(f"/api/v1/products/{product_id}", headers=admin_headers)
        assert del_ok.status_code == 204


@pytest.mark.asyncio
async def test_packing_simulation_and_parallel_fleet_endpoints():
    """Valida simulação 3D assíncrona, simulação paralela de frota, bloqueio RBAC (403) e proteção anti-DoS (422)."""
    await init_db()
    await seed_initial_data()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        logistica_headers = _auth_header("logistica@bamboo.com", "LOGISTICA")
        vendas_headers = _auth_header("vendas@bamboo.com", "VENDAS")

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

        # 1. [CASO NEGATIVO - NÃO PASSA] Usuário VENDAS tentando usar otimizador logístico 3D -> 403 Forbidden
        res_forbidden = await client.post("/api/v1/logistics/pack-simulation", headers=vendas_headers, json=payload)
        assert res_forbidden.status_code == 403

        # 2. [CASO NEGATIVO - NÃO PASSA] Tentativa de DoS algorítmico com quantity=10000 (> 500) -> 422 Unprocessable Entity
        dos_payload = {
            **payload,
            "items": [
                {"name": "Ataque DoS", "quantity": 10000, "length_m": 1.0, "width_m": 1.0, "height_m": 1.0, "weight_kg": 10.0}
            ]
        }
        res_dos = await client.post("/api/v1/logistics/pack-simulation", headers=logistica_headers, json=dos_payload)
        assert res_dos.status_code == 422

        # 3. [CASO POSITIVO - PASSA] Simulação individual com papel LOGISTICA -> 200 OK
        res = await client.post("/api/v1/logistics/pack-simulation", headers=logistica_headers, json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "volumetric_efficiency_pct" in data
        assert "allocated_boxes" in data
        assert len(data["allocated_boxes"]) == 2

        # 4. [CASO POSITIVO - PASSA] Simulação Paralela Multi-Core da Frota Completa -> 200 OK
        fleet_res = await client.post(
            "/api/v1/logistics/pack-fleet-parallel",
            headers=logistica_headers,
            json={"items": payload["items"]}
        )
        assert fleet_res.status_code == 200
        fleet_data = fleet_res.json()
        assert fleet_data["parallel_workers_used"] == 3
        assert len(fleet_data["fleet_simulations"]) == 3
        assert fleet_data["recommended_vehicle"] in {"Toco Urbano", "Truck Baú", "Carreta LS"}
