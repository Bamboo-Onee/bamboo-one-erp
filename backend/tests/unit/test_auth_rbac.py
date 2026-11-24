"""Testes Unitários e de Integração de Autenticação JWT, Prevenção de Escalada de Privilégio e RBAC."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app, seed_initial_data
from src.core.database import init_db
from src.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing_and_verification():
    """Valida segurança do hashing com salt do bcrypt (Caso Positivo e Negativo)."""
    raw_pwd = "MinhaSenhaSuperSecreta@2026"
    pwd_hash = hash_password(raw_pwd)

    assert pwd_hash != raw_pwd
    assert verify_password(raw_pwd, pwd_hash) is True
    assert verify_password("SenhaIncorreta", pwd_hash) is False


def test_jwt_token_generation_and_decoding():
    """Valida assinatura e extração de claims em tokens JWT e rejeição de token adulterado."""
    payload = {"sub": "operador@bamboo.com", "name": "Operador", "role": "LOGISTICA"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "operador@bamboo.com"
    assert decoded["role"] == "LOGISTICA"
    assert "exp" in decoded

    # Caso Negativo: token adulterado não deve passar na verificação HMAC-SHA256
    assert decode_access_token(token + "adulterado") is None


@pytest.mark.asyncio
async def test_auth_login_privilege_escalation_block_and_rbac():
    """Valida ciclo completo: seed, bloqueio de escalada de privilégio (403), role inválida (400), login e RBAC."""
    await init_db()
    await seed_initial_data()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unique_id = uuid.uuid4().hex[:6]
        admin_email = f"admin_{unique_id}@bamboo.com"
        vendas_email = f"vendas_{unique_id}@bamboo.com"
        hacker_email = f"hacker_{unique_id}@bamboo.com"

        # 1. [CASO NEGATIVO - NÃO PASSA] Tentativa anônima de escalada de privilégio registrando-se como ADMIN -> 403
        res_escalation = await client.post("/api/v1/auth/register", json={
            "name": "Atacante Externo",
            "email": hacker_email,
            "password": "senhaHacker123",
            "role": "ADMIN"
        })
        assert res_escalation.status_code == 403
        assert "Escalada de privilégio bloqueada" in res_escalation.json()["detail"]

        # 2. [CASO NEGATIVO - NÃO PASSA] Tentativa de registro com papel (role) inexistente -> 400
        res_invalid_role = await client.post("/api/v1/auth/register", json={
            "name": "Role Inválida",
            "email": hacker_email,
            "password": "senhaHacker123",
            "role": "SUPER_ROOT"
        })
        assert res_invalid_role.status_code == 400

        # 3. [CASO POSITIVO - PASSA] Login do ADMIN master do seed para autorizar criação de novo ADMIN
        res_master_login = await client.post("/api/v1/auth/login", json={
            "email": "admin@bamboo.com",
            "password": "admin123"
        })
        assert res_master_login.status_code == 200
        master_token = res_master_login.json()["access_token"]

        # 4. [CASO POSITIVO - PASSA] ADMIN autenticado registra novo usuário ADMIN -> 201
        res_reg = await client.post(
            "/api/v1/auth/register",
            headers={"Authorization": f"Bearer {master_token}"},
            json={
                "name": "Administrador Teste",
                "email": admin_email,
                "password": "senhaAdmin123",
                "role": "ADMIN"
            }
        )
        assert res_reg.status_code == 201

        # 5. [CASO NEGATIVO - NÃO PASSA] E-mail duplicado no registro -> 400
        res_dup = await client.post("/api/v1/auth/register", json={
            "name": "Duplicado",
            "email": admin_email,
            "password": "senhaAdmin123",
            "role": "VENDAS"
        })
        assert res_dup.status_code == 400

        # 6. [CASO POSITIVO - PASSA] Auto-registro de usuário operacional VENDAS -> 201
        res_reg_v = await client.post("/api/v1/auth/register", json={
            "name": "Vendedor Teste",
            "email": vendas_email,
            "password": "senhaVendas123",
            "role": "VENDAS"
        })
        assert res_reg_v.status_code == 201

        # 7. [CASO NEGATIVO - NÃO PASSA] Login com senha errada -> 401
        res_fail = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "senhaErrada"
        })
        assert res_fail.status_code == 401

        # 8. [CASO POSITIVO - PASSA] Login com sucesso ADMIN e VENDAS
        res_login_admin = await client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "senhaAdmin123"
        })
        assert res_login_admin.status_code == 200
        admin_token = res_login_admin.json()["access_token"]

        res_login_vendas = await client.post("/api/v1/auth/login", json={
            "email": vendas_email,
            "password": "senhaVendas123"
        })
        assert res_login_vendas.status_code == 200
        vendas_token = res_login_vendas.json()["access_token"]

        # 9. [CASO NEGATIVO - NÃO PASSA] Usuário VENDAS tentando registrar um ADMIN -> 403
        res_vendas_esc = await client.post(
            "/api/v1/auth/register",
            headers={"Authorization": f"Bearer {vendas_token}"},
            json={
                "name": "Tentativa Escalada Vendas",
                "email": f"esc_{unique_id}@bamboo.com",
                "password": "senha123",
                "role": "ADMIN"
            }
        )
        assert res_vendas_esc.status_code == 403

        # 10. Endpoint /auth/me com token válido -> 200
        res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_me.status_code == 200
        assert res_me.json()["email"] == admin_email

        # 11. Endpoint restrito a ADMIN (/auth/users):
        # Sem token -> 401
        res_no_token = await client.get("/api/v1/auth/users")
        assert res_no_token.status_code == 401

        # Com usuário VENDAS -> 403 Forbidden
        res_forbidden = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {vendas_token}"})
        assert res_forbidden.status_code == 403

        # Com usuário ADMIN -> 200 OK
        res_allowed = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_allowed.status_code == 200
        assert len(res_allowed.json()) >= 2
