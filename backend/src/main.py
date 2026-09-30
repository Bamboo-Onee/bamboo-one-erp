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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia inicialização e encerramento de recursos compartilhados (banco, pools, brokers)."""
    print(f"[STARTUP] Iniciando {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    try:
        await init_db()
        print("[STARTUP] Todas as tabelas do banco consolidado foram inicializadas com sucesso.")

        # Seed inicial de usuários com senhas criptografadas por bcrypt se admin não existir
        async with async_session_factory() as session:
            stmt = select(src.core.models.UserORM).where(src.core.models.UserORM.email == "admin@bamboo.com")
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                admin_user = src.core.models.UserORM(
                    name="Administrador Master",
                    email="admin@bamboo.com",
                    password_hash=hash_password("admin123"),
                    role="ADMIN",
                    is_active=True
                )
                log_user = src.core.models.UserORM(
                    name="Operador Logístico",
                    email="logistica@bamboo.com",
                    password_hash=hash_password("logistica123"),
                    role="LOGISTICA",
                    is_active=True
                )
                vend_user = src.core.models.UserORM(
                    name="Representante Comercial",
                    email="vendas@bamboo.com",
                    password_hash=hash_password("vendas123"),
                    role="VENDAS",
                    is_active=True
                )
                session.add_all([admin_user, log_user, vend_user])
                await session.commit()
                print("[STARTUP] Usuários padrão criados: admin@bamboo.com, logistica@bamboo.com, vendas@bamboo.com.")
    except Exception as e:
        print(f"[WARN] Erro ao inicializar banco: {e}")
    yield
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

# Configuração de CORS para comunicação segura com o Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
