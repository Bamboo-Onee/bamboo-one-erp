"""Testes de Integração e Unidade para os Módulos Consolidados do Grupo Bamboo:

- Compras Nacionais
- Importações
- Estoque & Movimentações
- Comercial / Vendas
- Entregas
- Financeiro
- RH
- AI Agent (Tool Calling)
"""

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.core.database import init_db


@pytest.mark.asyncio
async def test_purchases_and_stock_flow():
    """Valida ciclo de criação de PO de compra e consulta de saldos de estoque."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        po_payload = {
            "supplier_name": "Fornecedor Alpha Teste",
            "items": [
                {"product_sku": "BAM-0082", "product_name": "Caixa Master A", "quantity": 10, "unit_price": 50.0}
            ]
        }
        res_po = await client.post("/api/v1/purchases", json=po_payload)
        assert res_po.status_code == 201
        po_data = res_po.json()
        assert po_data["total_amount"] == 500.0
        assert "PO-" in po_data["po_number"]

        # Estoque
        res_stock = await client.get("/api/v1/stock/balances")
        assert res_stock.status_code == 200
        assert len(res_stock.json()) > 0


@pytest.mark.asyncio
async def test_sales_and_finance_flow():
    """Valida criação de pedido de venda e lançamentos financeiros."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Venda
        sale_payload = {
            "customer_name": "Cliente Exemplo Teste",
            "representative_name": "Vendedor 1",
            "items": [
                {"product_sku": "BAM-0082", "product_name": "Caixa Master A", "quantity": 5, "unit_price": 100.0}
            ]
        }
        res_sale = await client.post("/api/v1/sales", json=sale_payload)
        assert res_sale.status_code == 201
        assert res_sale.json()["total_amount"] == 500.0

        # Financeiro resumo
        res_fin = await client.get("/api/v1/finance/summary")
        assert res_fin.status_code == 200
        data = res_fin.json()
        assert "total_payable" in data
        assert "total_receivable" in data


@pytest.mark.asyncio
async def test_ai_agent_tool_calling():
    """Valida se o AI Agent aciona o Tool Calling para o cálculo de 3D Bin Packing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat_payload = {
            "prompt": "Quantas caixas padrão cabem no baú do Truck?",
            "truck_name": "Truck Baú"
        }
        res_ai = await client.post("/api/v1/ai/chat", json=chat_payload)
        assert res_ai.status_code == 200
        data = res_ai.json()
        assert data["tool_called"] == "calculate_truck_packing"
        assert "volumetric_efficiency_pct" in data["tool_result"]
        assert "Olá! Analisei sua solicitação" in data["reply"]
