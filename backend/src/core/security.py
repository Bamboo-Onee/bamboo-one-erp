"""Módulo de Segurança, Criptografia e Gerenciamento de Tokens JWT.

Implementa padrões OWASP:
- Hashing de senhas com bcrypt e salt aleatório
- Assinatura e verificação de tokens JWT com expiração configurada
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import bcrypt
import jwt

from src.config.settings import settings

SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "bamboo_super_secret_jwt_key_2026_x98z7a")
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)  # 24 horas


def hash_password(password: str) -> str:
    """Gera hash seguro de senha utilizando bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash armazenado."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Gera um token JWT assinado contendo claims do usuário e prazo de expiração."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica e valida assinatura e expiração de um token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
