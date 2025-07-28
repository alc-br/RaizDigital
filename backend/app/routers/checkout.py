"""
Routes related to payment and checkout sessions.

This router exposes an endpoint to create a Stripe Checkout session for
a given order.  The price can be supplied either via a predefined
Stripe price ID or dynamically using the order's price.  The session
metadata stores the order ID so that the webhook can correlate the
payment with the search order.
"""
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_session
from ..models import SearchOrder


class CheckoutSessionCreateRequest(BaseModel):
    order_id: int


router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/create-session")
async def create_checkout_session(
    body: CheckoutSessionCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Create a Stripe Checkout session for the specified order."""
    settings = get_settings()
    stripe.api_key = settings.stripe_api_key
    order = await session.get(SearchOrder, body.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    # Only allow payment when the order is pending payment
    from ..models import OrderStatus  # imported here to avoid circular import
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not awaiting payment")
    # Determine price
    line_item: dict[str, any]
    if settings.stripe_price_id:
        line_item = {
            "price": settings.stripe_price_id,
            "quantity": 1,
        }
    else:
        # Dynamically create price data in BRL
        line_item = {
            "price_data": {
                "currency": "brl",
                "product_data": {"name": f"Busca de Certidão ({order.target_name})"},
                "unit_amount": int(order.order_price * 100),
            },
            "quantity": 1,
        }
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[line_item],
            mode="payment",
            success_url=settings.api_base_url + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.api_base_url + "/cancel",
            metadata={"order_id": str(order.id)},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Save session ID on order
    order.stripe_session_id = checkout_session.id
    await session.commit()
    return {"id": checkout_session.id, "url": checkout_session.url}
