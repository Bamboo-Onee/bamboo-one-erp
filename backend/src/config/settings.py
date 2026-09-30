"""Módulo de Configuração e Variáveis de Ambiente da Aplicação.

Utiliza Pydantic Settings para validação estrita de tipos e injeção automática de variáveis de ambiente.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Aplicação
    PROJECT_NAME: str = "CRM Logístico Inteligente - Grupo Bamboo"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development, staging, production")
    LOG_LEVEL: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR")

    # Banco de Dados Assíncrono (PostgreSQL + asyncpg)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres_secure_pass_2026@localhost:5432/crm_logistico_db",
        description="String de conexão assíncrona SQLAlchemy"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Segurança, Criptografia e JWT (OWASP)
    SECRET_KEY: str = Field(
        default="bamboo_enterprise_hyper_secure_jwt_secret_key_2026_change_in_production",
        description="Chave de assinatura HMAC-SHA256"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Chaves de API para IA (Tool Calling)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""


# Instância global singleton das configurações
settings = Settings()
