"""
Security utilities for password hashing and JWT authentication.

This module uses Passlib's ``CryptContext`` to hash and verify
passwords securely.  JWT tokens are generated and verified using
``python-jose``; tokens carry the user ID and expire after a
configurable duration.
"""
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check that a plaintext password matches its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def create_token(*, data: dict, expires_delta: timedelta) -> str:
    """Generate a JWT token with a specific expiration interval."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_access_token(*, data: dict, expires_minutes: Optional[int] = None) -> str:
    """Generate a short‑lived access token."""
    settings = get_settings()
    minutes = expires_minutes or settings.access_token_expire_minutes
    return create_token(data=data, expires_delta=timedelta(minutes=minutes))


def create_refresh_token(*, data: dict, expires_days: int = 7) -> str:
    """Generate a long‑lived refresh token.  Defaults to 7 days."""
    return create_token(data=data, expires_delta=timedelta(days=expires_days))


def verify_token(token: str) -> Optional[int]:
    """Decode a JWT token and return the user ID if valid.

    Returns ``None`` if the token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id: int = int(payload.get("user_id"))
        return user_id
    except (JWTError, ValueError, TypeError):
        return None
