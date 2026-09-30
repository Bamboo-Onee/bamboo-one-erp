"""Testes Unitários e de Integração de Autenticação JWT e RBAC (Role-Based Access Control)."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.core.database import init_db
from src.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing_and_verification():
    """Valida segurança do hashing com salt do bcrypt."""
    raw_pwd = "MinhaSenhaSuperSecreta@2026"
    pwd_hash = hash_password(raw_pwd)

    assert pwd_hash != raw_pwd
    assert verify_password(raw_pwd, pwd_hash) is True
    assert verify_password("SenhaIncorreta", pwd_hash) is False


def test_jwt_token_generation_and_decoding():
    """Valida assinatura e extração de claims em tokens JWT."""
    payload = {"sub": "operador@bamboo.com", "name": "Operador", "role": "LOGISTICA"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "operador@bamboo.com"
    assert decoded["role"] == "LOGISTICA"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_auth_login_and_rbac_protection():
    """Valida ciclo completo: registro, login, acesso protegido e bloqueio RBAC 403."""
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unique_id = uuid.uuid4().hex[:6]
        admin_email = f"admin_{unique_id}@bamboo.com"
        vendas_email = f"vendas_{unique_id}@bamboo.com"

        # 1. Registra usuário ADMIN
        res_reg = await client.post("/api/v1/auth/register", json={
            "name": "Administrador Teste",
            "email": admin_email,
            "password": "senhaAdmin123",
            "role": "ADMIN"
        })
        assert res_reg.status_code == 201

        # 2. Registra usuário VENDAS
        res_reg_v = await client.post("/api/v1/auth/register", json={
            "name": "Vendedor Teste",
            "email": vendas_email,
            "password": "senhaVendas123",
            "role": "VENDAS"
        })
        assert res_reg_v.status_code == 201

        # 3. Login com senha errada -> 401
        res_fail = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "senhaErrada"
        })
        assert res_fail.status_code == 401

        # 4. Login com sucesso ADMIN
        res_login_admin = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "senhaAdmin123"
        })
        assert res_login_admin.status_code == 200
        admin_token = res_login_admin.json()["access_token"]
        assert admin_token is not None

        # 5. Login com sucesso VENDAS
        res_login_vendas = await client.post("/api/v1/auth/login", json={
            "email": vendas_email,
            "password": "senhaVendas123"
        })
        assert res_login_vendas.status_code == 200
        vendas_token = res_login_vendas.json()["access_token"]

        # 6. Endpoint /auth/me com token válido
        res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_me.status_code == 200
        assert res_me.json()["email"] == admin_email

        # 7. Endpoint restrito a ADMIN (/auth/users):
        # Acesso sem token -> 401
        res_no_token = await client.get("/api/v1/auth/users")
        assert res_no_token.status_code == 401

        # Acesso com usuário VENDAS -> 403 Forbidden
        res_forbidden = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {vendas_token}"})
        assert res_forbidden.status_code == 403

        # Acesso com usuário ADMIN -> 200 OK
        res_allowed = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_allowed.status_code == 200
        assert len(res_allowed.json()) >= 2
