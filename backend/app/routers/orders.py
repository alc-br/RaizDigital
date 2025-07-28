"""
Endpoints for managing search orders.

Users can create orders, view their existing orders, and retrieve
details of a specific order including its search results.  The actual
processing of orders is handled asynchronously after payment via
Stripe and Celery; this router only manages the state stored in the
database.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_session
from ..dependencies import get_current_user


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.SearchOrderOut, status_code=201)
async def create_order(
    order_in: schemas.SearchOrderCreate,
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new search order with status ``PENDING_PAYMENT``."""
    order = models.SearchOrder(
        user_id=current_user.id,
        status=models.OrderStatus.PENDING_PAYMENT,
        order_price=order_in.order_price,
        target_name=order_in.target_name,
        target_dob_approx=order_in.target_dob_approx,
        target_city=order_in.target_city,
        target_state=order_in.target_state,
        target_parents_names=order_in.target_parents_names,
        additional_info=order_in.additional_info,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


@router.get("/", response_model=list[schemas.SearchOrderOut])
async def list_orders(
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List all search orders belonging to the authenticated user."""
    result = await session.execute(
        select(models.SearchOrder).where(models.SearchOrder.user_id == current_user.id).order_by(models.SearchOrder.created_at.desc())
    )
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=schemas.SearchOrderOut)
async def get_order_detail(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Retrieve detailed information about a specific order and its results."""
    order = await session.get(models.SearchOrder, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
