"""Ponto de entrada principal da aplicação FastAPI.

Configura middlewares, ciclo de vida (lifespan), documentação OpenAPI, segurança e todos os roteadores modulares.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from src.config.settings import settings
from src.core.database import init_db, async_session_factory
from src.core.security import hash_password
import src.core.models  # Importa para registrar todos os modelos ORM no metadata
from src.modules.logistics.domain.services.packing_service import PackingService

# Roteadores de todos os módulos consolidados
from src.modules.auth.presentation.routes.auth_routes import router as auth_router
from src.modules.cadastros_mestres.presentation.routes.cadastros_routes import router as cadastros_router
from src.modules.logistics.presentation.routes.logistics_routes import router as logistics_router
from src.modules.compras.presentation.routes.compras_routes import router as compras_router
from src.modules.importacoes.presentation.routes.importacoes_routes import router as importacoes_router
from src.modules.estoque.presentation.routes.estoque_routes import router as estoque_router
from src.modules.crm.presentation.routes.sales_routes import router as sales_router
from src.modules.producao_expedicao.presentation.routes.deliveries_routes import router as deliveries_router
from src.modules.financeiro.presentation.routes.finance_routes import router as finance_router
from src.modules.rh.presentation.routes.rh_routes import router as rh_router
from src.modules.ai_agent.presentation.routes.ai_routes import router as ai_router


async def seed_initial_data() -> None:
    """Centraliza o seed inicial de usuários e dados demonstrativos fora das rotas GET."""
    async with async_session_factory() as session:
        # 1. Usuários padrão
        stmt = select(src.core.models.UserORM).where(src.core.models.UserORM.email == "admin@bamboo.com")
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            session.add_all([
                src.core.models.UserORM(
                    name="Administrador Master",
                    email="admin@bamboo.com",
                    password_hash=hash_password("admin123"),
                    role="ADMIN",
                    is_active=True
                ),
                src.core.models.UserORM(
                    name="Operador Logístico",
                    email="logistica@bamboo.com",
                    password_hash=hash_password("logistica123"),
                    role="LOGISTICA",
                    is_active=True
                ),
                src.core.models.UserORM(
                    name="Representante Comercial",
                    email="vendas@bamboo.com",
                    password_hash=hash_password("vendas123"),
                    role="VENDAS",
                    is_active=True
                ),
            ])

        # 2. Saldos iniciais de estoque
        res_stock = await session.execute(select(src.core.models.StockBalanceORM).limit(1))
        if not res_stock.scalar_one_or_none():
            session.add_all([
                src.core.models.StockBalanceORM(product_sku="BAM-0082", product_name="Caixa Master A", warehouse_name="CD Principal", quantity_available=138, quantity_reserved=24),
                src.core.models.StockBalanceORM(product_sku="BAM-0154", product_name="Pallet B", warehouse_name="CD Principal", quantity_available=34, quantity_reserved=8),
                src.core.models.StockBalanceORM(product_sku="BAM-0221", product_name="Volume Frágil", warehouse_name="CD Principal", quantity_available=52, quantity_reserved=12),
            ])

        # 3. Pedidos de venda
        res_sales = await session.execute(select(src.core.models.SalesOrderORM).limit(1))
        if not res_sales.scalar_one_or_none():
            session.add_all([
                src.core.models.SalesOrderORM(order_number="VEN-2026-0081", customer_name="Cliente Atlântico Ltda", total_amount=78200.0, status="Em separação"),
                src.core.models.SalesOrderORM(order_number="VEN-2026-0080", customer_name="Distribuidora Sul", total_amount=43150.0, status="Expedido"),
            ])

        # 4. Entregas / Expedição
        res_deliv = await session.execute(select(src.core.models.DeliveryORM).limit(1))
        if not res_deliv.scalar_one_or_none():
            session.add_all([
                src.core.models.DeliveryORM(delivery_number="ENT-00618", customer_name="Cliente Atlântico Ltda", destination_city="Recife/PE", total_volumes=44, vehicle_plate="BRA-2E19", status="Carga pronta"),
                src.core.models.DeliveryORM(delivery_number="ENT-00617", customer_name="Cliente Horizonte", destination_city="Jaboatão/PE", total_volumes=28, vehicle_plate="PE-9812", status="Em rota"),
            ])

        # 5. Lançamentos Financeiros
        res_fin = await session.execute(select(src.core.models.FinancialEntryORM).limit(1))
        if not res_fin.scalar_one_or_none():
            session.add_all([
                src.core.models.FinancialEntryORM(entry_type="PAGAR", description="Fornecedor de Pallets", entity_name="Bamboo Trade", category="Compras", amount=18430.0, due_date="15/09/2026", status="Pendente"),
                src.core.models.FinancialEntryORM(entry_type="PAGAR", description="Frete Internacional Santos", entity_name="Maersk Line", category="Importação", amount=12850.0, due_date="18/09/2026", status="Pendente"),
                src.core.models.FinancialEntryORM(entry_type="RECEBER", description="Venda Comercial Atlântico", entity_name="Cliente Atlântico", category="Vendas", amount=78200.0, due_date="20/09/2026", status="Pendente"),
                src.core.models.FinancialEntryORM(entry_type="RECEBER", description="Venda Distribuidora Sul", entity_name="Distribuidora Sul", category="Vendas", amount=43150.0, due_date="22/09/2026", status="Pendente"),
            ])

        # 6. Funcionários (RH)
        res_emp = await session.execute(select(src.core.models.EmployeeORM).limit(1))
        if not res_emp.scalar_one_or_none():
            session.add_all([
                src.core.models.EmployeeORM(name="Marina Silva", cpf="111.222.333-44", role="Analista de Importação", department="Comércio Exterior", salary=6200.0, admission_date="15/03/2023", status="Ativo"),
                src.core.models.EmployeeORM(name="Carlos Eduardo", cpf="555.666.777-88", role="Supervisor de Estoque", department="Logística", salary=5400.0, admission_date="10/01/2022", status="Ativo"),
                src.core.models.EmployeeORM(name="Fernanda Lima", cpf="999.888.777-66", role="Coordenadora Financeira", department="Financeiro", salary=8900.0, admission_date="01/08/2021", status="Férias"),
            ])

        try:
            await session.commit()
        except Exception:
            await session.rollback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia inicialização e encerramento de recursos compartilhados (banco, pools, brokers)."""
    print(f"[STARTUP] Iniciando {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    init_pool = getattr(PackingService, "init_process_pool", None)
    if callable(init_pool):
        init_pool()
    try:
        await init_db()
        print("[STARTUP] Todas as tabelas do banco consolidado foram inicializadas com sucesso.")

        if settings.ENVIRONMENT != "production":
            await seed_initial_data()
            print("[STARTUP] Seed inicial verificado/concluído com sucesso.")
    except Exception as e:
        print(f"[WARN] Erro ao inicializar banco: {e}")
    yield
    shutdown_pool = getattr(PackingService, "shutdown_process_pool", None)
    if callable(shutdown_pool):
        shutdown_pool()
    print(f"[SHUTDOWN] Encerrando {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API do Sistema Integrado de Gestão e Otimizador 3D de Carga - Grupo Bamboo. "
        "Construído sob Monolito Modular em Clean Architecture com TDD e validações OWASP."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração estrita de CORS parametrizada via settings (OWASP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Registro de Todos os Roteadores da Aplicação
app.include_router(auth_router)
app.include_router(cadastros_router)
app.include_router(logistics_router)
app.include_router(compras_router)
app.include_router(importacoes_router)
app.include_router(estoque_router)
app.include_router(sales_router)
app.include_router(deliveries_router)
app.include_router(finance_router)
app.include_router(rh_router)
app.include_router(ai_router)


@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check():
    """Endpoint de verificação de integridade e disponibilidade da API."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }