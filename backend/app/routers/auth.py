"""
Authentication endpoints for RaizDigital.

This router implements user registration and login.  Passwords are
hashed before storage, and successful logins return a JWT access
token.  The login endpoint uses the standard OAuth2 password grant.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
import secrets
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_session
from ..utils import security
from ..config import get_settings
from ..tasks_utils import send_email_task
from ..models import PasswordResetToken


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
async def register_user(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user with an email and password.

    Returns the created user object (without the password).
    """
    # Check if the email is already taken
    result = await session.execute(select(models.User).where(models.User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = security.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, full_name=user_in.full_name, password_hash=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    # Send welcome email asynchronously
    subject = "Bem-vindo ao RaizDigital"
    body = (
        f"Olá {user.full_name or user.email},\n\n"
        "Obrigado por se registrar no RaizDigital. Agora você pode iniciar suas buscas de certidões diretamente pelo seu painel.\n\n"
        "Atenciosamente,\nEquipe RaizDigital"
    )
    send_email_task.delay(user.email, subject, body)
    return user


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """Authenticate a user and return a JWT token on success."""
    result = await session.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create access and refresh tokens
    access_token = security.create_access_token(data={"user_id": user.id})
    refresh_token = security.create_refresh_token(data={"user_id": user.id})
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/forgot-password")
async def forgot_password(request: schemas.ForgotPasswordRequest, session: AsyncSession = Depends(get_session)) -> dict:
    """Initiate the password reset process by emailing a reset link."""
    result = await session.execute(select(models.User).where(models.User.email == request.email))
    user = result.scalar_one_or_none()
    # Always return success to avoid exposing whether an email exists
    if user:
        token = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        prt = models.PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        session.add(prt)
        await session.commit()
        # Build a link to the frontend reset password page. Use the
        # FRONTEND_BASE_URL to ensure the link points to the user‑facing
        # application instead of the API.
        reset_link = f"{get_settings().frontend_base_url}/redefinir-senha/{token}"
        subject = "Redefinição de senha"
        body = (
            f"Olá {user.full_name or user.email},\n\n"
            "Recebemos uma solicitação para redefinir sua senha. Para criar uma nova senha, clique no link abaixo:\n"
            f"{reset_link}\n\n"
            "Se você não solicitou esta redefinição, ignore este e-mail.\n\n"
            "Atenciosamente,\nEquipe RaizDigital"
        )
        send_email_task.delay(user.email, subject, body)
    return {"detail": "Se o e-mail estiver registrado, enviaremos instruções de redefinição"}


@router.post("/reset-password")
async def reset_password(request: schemas.ResetPasswordRequest, session: AsyncSession = Depends(get_session)) -> dict:
    """Reset the user's password using a valid reset token."""
    # Find the reset token
    result = await session.execute(
        select(models.PasswordResetToken).where(models.PasswordResetToken.token == request.token)
    )
    token_row = result.scalar_one_or_none()
    if not token_row or token_row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    user = await session.get(models.User, token_row.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # Update password
    user.password_hash = security.get_password_hash(request.new_password)
    # Delete token
    await session.delete(token_row)
    await session.commit()
    return {"detail": "Senha redefinida com sucesso"}


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(token: str) -> schemas.Token:
    """Generate a new access token using a valid refresh token."""
    user_id = security.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = security.create_access_token(data={"user_id": user_id})
    refresh_token = security.create_refresh_token(data={"user_id": user_id})
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)
