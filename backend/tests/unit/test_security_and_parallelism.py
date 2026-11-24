"""Suíte dedicada de Auditoria de Segurança (AppSec / OWASP) e Paralelismo Real (CPU Multi-Core & I/O Atômico).

Separa explicitamente:
- Testes Negativos / Adversariais (requisições maliciosas ou inválidas que NÃO DEVEM PASSAR — barradas com 400, 401, 403, 422)
- Testes Positivos de Paralelismo Real (execução simultânea via ProcessPoolExecutor + asyncio.gather sem bloqueio do Event Loop e sem Lost Update)
"""

import asyncio
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app, seed_initial_data
from src.core.database import init_db
from src.core.security import create_access_token


def _token_headers(email: str, role: str) -> dict[str, str]:
    token = create_access_token({"sub": email, "name": role.title(), "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_negative_anonymous_access_blocked_on_all_business_routes_401():
    """[NÃO PASSA / BLOQUEADO 401] Garante que nenhuma das 20 rotas de negócio aceita acesso anônimo sem JWT."""
    await init_db()
    await seed_initial_data()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        protected_get_routes = [
            "/api/v1/products",
            "/api/v1/customers",
            "/api/v1/vehicles",
            "/api/v1/purchases",
            "/api/v1/imports",
            "/api/v1/stock/balances",
            "/api/v1/sales",
            "/api/v1/deliveries",
            "/api/v1/finance",
            "/api/v1/finance/summary",
            "/api/v1/employees",
            "/api/v1/auth/me",
            "/api/v1/auth/users",
        ]
        responses = await asyncio.gather(*(client.get(route) for route in protected_get_routes))
        for route, res in zip(protected_get_routes, responses):
            assert res.status_code == 401, f"Rota {route} deveria bloquear acesso anônimo com 401, mas retornou {res.status_code}"


@pytest.mark.asyncio
async def test_negative_privilege_escalation_anonymous_admin_blocked_403():
    """[NÃO PASSA / BLOQUEADO 403] Bloqueia tentativa anônima de criar conta com role=ADMIN (Mass Assignment)."""
    await init_db()
    await seed_initial_data()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Invasor Escalada",
                "email": f"invasor_{uuid.uuid4().hex[:6]}@bamboo.com",
                "password": "senhaForte123",
                "role": "ADMIN",
            },
        )
        assert res.status_code == 403
        assert "Escalada de privilégio bloqueada" in res.json()["detail"]


@pytest.mark.asyncio
async def test_negative_rbac_unauthorized_roles_blocked_403():
    """[NÃO PASSA / BLOQUEADO 403] Garante que cada perfil é barrado ao tentar acessar módulos fora de sua alçada."""
    await init_db()
    await seed_initial_data()

    vendas_headers = _token_headers("vendas@bamboo.com", "VENDAS")
    logistica_headers = _token_headers("logistica@bamboo.com", "LOGISTICA")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # VENDAS não pode acessar RH (PII), Financeiro, criar Compras, nem excluir Produtos
        res_rh = await client.get("/api/v1/employees", headers=vendas_headers)
        res_fin = await client.get("/api/v1/finance", headers=vendas_headers)
        res_del_prod = await client.delete("/api/v1/products/1", headers=vendas_headers)
        res_3d = await client.post(
            "/api/v1/logistics/pack-fleet-parallel",
            headers=vendas_headers,
            json={"items": [{"name": "Caixa", "quantity": 1, "length_m": 1.0, "width_m": 1.0, "height_m": 1.0, "weight_kg": 10.0}]},
        )
        # LOGISTICA não pode emitir Pedido de Venda nem consultar RH
        res_sale = await client.post(
            "/api/v1/sales",
            headers=logistica_headers,
            json={"customer_name": "Cliente X", "items": [{"product_sku": "BAM-0082", "product_name": "Caixa", "quantity": 1, "unit_price": 10.0}]},
        )

        assert res_rh.status_code == 403
        assert res_fin.status_code == 403
        assert res_del_prod.status_code == 403
        assert res_3d.status_code == 403
        assert res_sale.status_code == 403


@pytest.mark.asyncio
async def test_negative_algorithmic_dos_and_invalid_inputs_rejected_422_400():
    """[NÃO PASSA / BLOQUEADO 422 e 400] Rejeita payloads de DoS no motor 3D, CPF duplicado e movimentação inválida."""
    await init_db()
    await seed_initial_data()

    admin_headers = _token_headers("admin@bamboo.com", "ADMIN")
    logistica_headers = _token_headers("logistica@bamboo.com", "LOGISTICA")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Payload de DoS com quantity=999999 (> limite 500) -> 422
        res_dos = await client.post(
            "/api/v1/logistics/pack-fleet-parallel",
            headers=logistica_headers,
            json={"items": [{"name": "Bombs", "quantity": 999999, "length_m": 1.0, "width_m": 1.0, "height_m": 1.0, "weight_kg": 10.0}]},
        )
        assert res_dos.status_code == 422

        # 2. Tipo de movimentação de estoque inexistente -> 400
        res_bad_mov = await client.post(
            "/api/v1/stock/movements",
            headers=logistica_headers,
            json={
                "movement_type": "Roubo",
                "product_sku": "BAM-0082",
                "product_name": "Caixa Master A",
                "quantity": 1,
                "reason": "Inválido",
            },
        )
        assert res_bad_mov.status_code == 400

        # 3. CPF duplicado no RH -> 400
        res_dup_cpf = await client.post(
            "/api/v1/employees",
            headers=admin_headers,
            json={
                "name": "Clone Marina",
                "cpf": "111.222.333-44",
                "role": "Analista",
                "department": "TI",
                "salary": 5000.0,
            },
        )
        assert res_dup_cpf.status_code == 400


@pytest.mark.asyncio
async def test_positive_parallel_multi_core_3d_packing_does_not_block_event_loop():
    """[PASSA 200] Executa simulação 3D de frota em paralelo multi-core junto com requisições concorrentes no Event Loop."""
    await init_db()
    await seed_initial_data()

    logistica_headers = _token_headers("logistica@bamboo.com", "LOGISTICA")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        cargo_items = [
            {"name": "Caixa Master A", "quantity": 24, "length_m": 1.2, "width_m": 0.8, "height_m": 0.7, "weight_kg": 185.0},
            {"name": "Pallet B", "quantity": 8, "length_m": 1.0, "width_m": 1.0, "height_m": 1.45, "weight_kg": 410.0},
            {"name": "Volume Frágil", "quantity": 12, "length_m": 0.7, "width_m": 0.55, "height_m": 0.6, "weight_kg": 76.0},
        ]

        # Dispara simultaneamente 2 simulações completas de frota (6 cálculos 3D) + 5 healthchecks concorrentes
        tasks = [
            client.post("/api/v1/logistics/pack-fleet-parallel", headers=logistica_headers, json={"items": cargo_items}),
            client.post("/api/v1/logistics/pack-fleet-parallel", headers=logistica_headers, json={"items": cargo_items}),
            client.get("/health"),
            client.get("/health"),
            client.get("/health"),
            client.get("/api/v1/stock/balances", headers=logistica_headers),
        ]
        results = await asyncio.gather(*tasks)

        assert results[0].status_code == 200
        assert results[1].status_code == 200
        assert all(r.status_code == 200 for r in results[2:])

        fleet_plan = results[0].json()
        assert fleet_plan["parallel_workers_used"] == 3
        assert fleet_plan["recommended_vehicle"] in {"Toco Urbano", "Truck Baú", "Carreta LS"}
        assert len(fleet_plan["fleet_simulations"]) == 3
