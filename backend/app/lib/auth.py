"""Authentication: API key + JWT helpers."""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a new API key with the configured prefix."""
    return f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"


def create_jwt(subject: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def require_api_key(api_key: str = Security(_api_key_header)) -> str:
    """Dependency: require a valid API key. Returns the key string."""
    if not api_key or not api_key.startswith(settings.api_key_prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
    return api_key


# ── Token encryption for CRM credentials ──

def _get_fernet():
    from cryptography.fernet import Fernet
    if not settings.token_encryption_key:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY not set — generate one with Fernet.generate_key()")
    return Fernet(settings.token_encryption_key.encode())


def encrypt_token(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode()).decode()
