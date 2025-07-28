"""
Routes for user profile management.

Provides endpoints for retrieving and updating the authenticated
user's profile.  Users can update their name and email, and change
their password by supplying the current password.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_session
from ..dependencies import get_current_user
from ..utils import security


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
async def get_profile(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Return the current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=schemas.UserOut)
async def update_profile(
    update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> models.User:
    """Update the authenticated user's profile."""
    # Update name and email if provided
    if update.email and update.email != current_user.email:
        # Check if new email already exists
        result = await session.execute(select(models.User).where(models.User.email == update.email))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="E-mail já está em uso")
        current_user.email = update.email
    if update.full_name is not None:
        current_user.full_name = update.full_name
    # Handle password change
    if update.new_password:
        if not update.current_password or not security.verify_password(update.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")
        current_user.password_hash = security.get_password_hash(update.new_password)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user