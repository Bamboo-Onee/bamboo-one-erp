"""Roteadores FastAPI e Dependências de Autenticação JWT e RBAC (Role-Based Access Control).

Implementa:
- Login seguro com geração de token JWT
- Registro de novos usuários com senha criptografada via bcrypt
- Dependência de extração do usuário autenticado (get_current_user)
- Dependência de proteção baseada em papéis (require_roles)
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import UserORM
from src.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação & RBAC"])
security_scheme = HTTPBearer(auto_error=False)


# ==============================================================================
# SCHEMAS / DTOS
# ==============================================================================
class UserLoginDTO(BaseModel):
    email: str = Field(..., description="E-mail de acesso corporativo")
    password: str = Field(..., description="Senha do usuário")


class UserRegisterDTO(BaseModel):
    name: str = Field(..., min_length=2, description="Nome completo")
    email: str = Field(..., description="E-mail corporativo único")
    password: str = Field(..., min_length=6, description="Senha segura")
    role: str = Field(default="LOGISTICA", description="ADMIN, LOGISTICA, VENDAS, COMPRAS, FINANCEIRO")


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO


# ==============================================================================
# DEPENDÊNCIAS RBAC
# ==============================================================================
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> UserORM:
    """Extrai, decodifica e valida o token JWT do header Authorization: Bearer <token>."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido ou inválido.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso expirado ou inválido.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    email = payload.get("sub")
    stmt = select(UserORM).where(UserORM.email == email)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário associado ao token não encontrado.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador."
        )

    return user


def require_roles(allowed_roles: List[str]):
    """Fábrica de dependência que valida se o usuário autenticado possui os papéis necessários (ADMIN possui acesso global)."""
    async def role_checker(current_user: UserORM = Depends(get_current_user)) -> UserORM:
        user_role = (current_user.role or "").upper()
        allowed = [r.upper() for r in allowed_roles]
        if "ADMIN" not in allowed:
            allowed.append("ADMIN")

        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Esta operação requer um dos seguintes papéis: {', '.join(allowed_roles)}."
            )
        return current_user

    return role_checker


# ==============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# ==============================================================================
@router.post("/login", response_model=TokenResponseDTO)
async def login(dto: UserLoginDTO, session: AsyncSession = Depends(get_db_session)):
    """Autentica o usuário corporativo e retorna o token JWT."""
    stmt = select(UserORM).where(UserORM.email == dto.email.strip().lower())
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(dto.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa. Contate o administrador do Grupo Bamboo."
        )

    token = create_access_token({
        "sub": user.email,
        "name": user.name,
        "role": user.role
    })

    return TokenResponseDTO(
        access_token=token,
        token_type="bearer",
        user=UserResponseDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(dto: UserRegisterDTO, session: AsyncSession = Depends(get_db_session)):
    """Cadastra um novo usuário corporativo no sistema com validação de e-mail único."""
    email_clean = dto.email.strip().lower()
    stmt = select(UserORM).where(UserORM.email == email_clean)
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário cadastrado com este e-mail."
        )

    new_user = UserORM(
        name=dto.name.strip(),
        email=email_clean,
        password_hash=hash_password(dto.password),
        role=dto.role.upper(),
        is_active=True
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserResponseDTO(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: UserORM = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado no token atual."""
    return UserResponseDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.get("/users", response_model=List[UserResponseDTO])
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    _: UserORM = Depends(require_roles(["ADMIN"]))
):
    """Lista todos os usuários corporativos (Restrito a Administradores)."""
    stmt = select(UserORM).order_by(UserORM.id.asc())
    res = await session.execute(stmt)
    users = res.scalars().all()
    return [
        UserResponseDTO(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]
