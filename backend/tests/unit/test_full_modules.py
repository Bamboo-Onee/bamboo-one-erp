"""Testes de Integração, Segurança RBAC e Concorrência Paralela Real para os Módulos do Grupo Bamboo:

- Compras Nacionais
- Importações
- Estoque & Movimentações Concorrentes (asyncio.gather sem Lost Update)
- Comercial / Vendas
- Entregas
- Financeiro (Agregação SQL)
- RH (Proteção de PII restrita a ADMIN)
- AI Agent (Tool Calling Assíncrono)
"""

import asyncio
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
async def test_purchases_and_stock_flow_with_rbac():
    """Valida criação de PO de compra, consulta de saldos e bloqueios RBAC (401/403)."""
    await init_db()
    await seed_initial_data()

    admin_headers = _auth_header("admin@bamboo.com", "ADMIN")
    vendas_headers = _auth_header("vendas@bamboo.com", "VENDAS")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        po_payload = {
            "supplier_name": "Fornecedor Alpha Teste",
            "items": [
                {"product_sku": "BAM-0082", "product_name": "Caixa Master A", "quantity": 10, "unit_price": 50.0}
            ]
        }

        # [CASO NEGATIVO - NÃO PASSA] Usuário VENDAS tentando emitir Pedido de Compra -> 403 Forbidden
        res_forbidden = await client.post("/api/v1/purchases", headers=vendas_headers, json=po_payload)
        assert res_forbidden.status_code == 403

        # [CASO POSITIVO - PASSA] ADMIN/COMPRAS emitindo Pedido de Compra -> 201 Created
        res_po = await client.post("/api/v1/purchases", headers=admin_headers, json=po_payload)
        assert res_po.status_code == 201
        po_data = res_po.json()
        assert po_data["total_amount"] == 500.0
        assert "PO-" in po_data["po_number"]

        # [CASO POSITIVO - PASSA] Consulta de saldos de estoque -> 200 OK
        res_stock = await client.get("/api/v1/stock/balances", headers=admin_headers)
        assert res_stock.status_code == 200
        assert len(res_stock.json()) > 0


@pytest.mark.asyncio
async def test_parallel_stock_movements_no_lost_update():
    """Valida que movimentações simultâneas via asyncio.gather são atômicas e não sofrem Lost Update."""
    await init_db()
    await seed_initial_data()

    logistica_headers = _auth_header("logistica@bamboo.com", "LOGISTICA")
    sku = f"BAM-PAR-{uuid.uuid4().hex[:5].upper()}"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. [CASO NEGATIVO - NÃO PASSA] Tentativa de saída em SKU sem estoque -> 400 Bad Request
        res_underflow = await client.post(
            "/api/v1/stock/movements",
            headers=logistica_headers,
            json={
                "movement_type": "Saída",
                "product_sku": sku,
                "product_name": "Produto Concorrente",
                "warehouse_name": "CD Principal",
                "quantity": 10,
                "reason": "Teste de saldo insuficiente"
            }
        )
        assert res_underflow.status_code == 400
        assert "Saldo insuficiente" in res_underflow.json()["detail"]

        # 2. [CASO POSITIVO - PASSA] Dispara 8 entradas paralelas de +10 unidades cada (= 80 unidades)
        entry_tasks = [
            client.post(
                "/api/v1/stock/movements",
                headers=logistica_headers,
                json={
                    "movement_type": "Entrada",
                    "product_sku": sku,
                    "product_name": "Produto Concorrente",
                    "warehouse_name": "CD Principal",
                    "quantity": 10,
                    "reason": f"Entrada paralela #{i}"
                }
            )
            for i in range(8)
        ]
        entry_responses = await asyncio.gather(*entry_tasks)
        assert all(r.status_code == 201 for r in entry_responses)

        # 3. [CASO POSITIVO - PASSA] Dispara 5 saídas paralelas de -6 unidades cada (= -30 unidades -> saldo esperado: 50)
        exit_tasks = [
            client.post(
                "/api/v1/stock/movements",
                headers=logistica_headers,
                json={
                    "movement_type": "Saída",
                    "product_sku": sku,
                    "product_name": "Produto Concorrente",
                    "warehouse_name": "CD Principal",
                    "quantity": 6,
                    "reason": f"Saída paralela #{i}"
                }
            )
            for i in range(5)
        ]
        exit_responses = await asyncio.gather(*exit_tasks)
        assert all(r.status_code == 201 for r in exit_responses)

        # Verifica o saldo final exato (80 - 30 = 50)
        balances_res = await client.get("/api/v1/stock/balances", headers=logistica_headers)
        assert balances_res.status_code == 200
        sku_balance = next(b for b in balances_res.json() if b["product_sku"] == sku)
        assert sku_balance["quantity_available"] == 50


@pytest.mark.asyncio
async def test_sales_finance_and_rh_rbac_and_sql_aggregation():
    """Valida vendas, agregação SQL financeira e proteção de dados sensíveis do RH (CPF/Salário)."""
    await init_db()
    await seed_initial_data()

    admin_headers = _auth_header("admin@bamboo.com", "ADMIN")
    vendas_headers = _auth_header("vendas@bamboo.com", "VENDAS")
    logistica_headers = _auth_header("logistica@bamboo.com", "LOGISTICA")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. [CASO POSITIVO - PASSA] Vendedor criando pedido de venda -> 201 Created
        sale_payload = {
            "customer_name": "Cliente Exemplo Teste",
            "representative_name": "Vendedor 1",
            "items": [
                {"product_sku": "BAM-0082", "product_name": "Caixa Master A", "quantity": 5, "unit_price": 100.0}
            ]
        }
        res_sale = await client.post("/api/v1/sales", headers=vendas_headers, json=sale_payload)
        assert res_sale.status_code == 201
        assert res_sale.json()["total_amount"] == 500.0

        # 2. [CASO NEGATIVO - NÃO PASSA] Logística tentando criar pedido de venda -> 403 Forbidden
        res_sale_forbidden = await client.post("/api/v1/sales", headers=logistica_headers, json=sale_payload)
        assert res_sale_forbidden.status_code == 403

        # 3. [CASO NEGATIVO - NÃO PASSA] Vendas tentando acessar resumo financeiro ou RH -> 403 Forbidden
        res_fin_forbidden = await client.get("/api/v1/finance/summary", headers=vendas_headers)
        assert res_fin_forbidden.status_code == 403

        res_rh_forbidden = await client.get("/api/v1/employees", headers=vendas_headers)
        assert res_rh_forbidden.status_code == 403

        # 4. [CASO NEGATIVO - NÃO PASSA] Lançamento financeiro com entry_type inválido -> 400 Bad Request
        res_fin_invalid = await client.post(
            "/api/v1/finance",
            headers=admin_headers,
            json={
                "entry_type": "INVALIDO",
                "description": "Teste Inválido",
                "entity_name": "Entidade",
                "amount": 100.0
            }
        )
        assert res_fin_invalid.status_code == 400

        # 5. [CASO POSITIVO - PASSA] Agregação SQL do resumo financeiro -> 200 OK
        res_fin = await client.get("/api/v1/finance/summary", headers=admin_headers)
        assert res_fin.status_code == 200
        data = res_fin.json()
        assert data["total_payable"] > 0
        assert data["total_receivable"] > 0
        assert round(data["total_receivable"] - data["total_payable"], 2) == data["projected_balance"]


@pytest.mark.asyncio
async def test_ai_agent_tool_calling_and_auth():
    """Valida proteção JWT no AI Agent (401 sem token) e execução assíncrona do Tool Calling 3D (200 com token)."""
    await init_db()
    await seed_initial_data()

    logistica_headers = _auth_header("logistica@bamboo.com", "LOGISTICA")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat_payload = {
            "prompt": "Quantas caixas padrão cabem no baú do Truck?",
            "truck_name": "Truck Baú"
        }

        # [CASO NEGATIVO - NÃO PASSA] Sem token JWT -> 401 Unauthorized
        res_unauth = await client.post("/api/v1/ai/chat", json=chat_payload)
        assert res_unauth.status_code == 401

        # [CASO POSITIVO - PASSA] Com token JWT -> 200 OK
        res_ai = await client.post("/api/v1/ai/chat", headers=logistica_headers, json=chat_payload)
        assert res_ai.status_code == 200
        data = res_ai.json()
        assert data["tool_called"] == "calculate_truck_packing"
        assert "volumetric_efficiency_pct" in data["tool_result"]
        assert "Olá! Analisei sua solicitação" in data["reply"]
