"""
Stripe webhook handler for payment events.

When a checkout session completes successfully, this endpoint is
invoked by Stripe.  It validates the signature, identifies the order
associated with the session (via metadata), updates the order status to
``PROCESSING`` and triggers the Celery task to start the search.
"""
import json
import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..config import get_settings
from .. import models
from ..tasks import process_search_order_task


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_session),
):
    """Handle Stripe webhook events.

    Only the ``checkout.session.completed`` event is of interest.  The
    order ID is expected to be stored in the Stripe session's
    ``metadata.order_id`` field.
    """
    settings = get_settings()
    payload = await request.body()
    sig_header = stripe_signature
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})
        order_id = metadata.get("order_id")
        if order_id is None:
            raise HTTPException(status_code=400, detail="Missing order_id in metadata")
        order = await session.get(models.SearchOrder, int(order_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        # Update status to PROCESSING and commit
        order.status = models.OrderStatus.PROCESSING
        await session.commit()
        # Send confirmation email to the user notifying that the search has started
        # We avoid importing tasks_utils here to prevent circular imports; import lazily
        from ..tasks_utils import send_email_task
        subject = "Sua busca foi iniciada"
        body = (
            f"Olá {order.user.full_name or order.user.email},\n\n"
            f"Recebemos o seu pagamento para a busca da certidão de {order.target_name}."
            "Nossa equipe e robôs estão iniciando a busca e enviaremos um e-mail quando estiver concluída.\n\n"
            "Atenciosamente,\nEquipe RaizDigital"
        )
        # Enqueue email sending via Celery
        send_email_task.delay(order.user.email, subject, body)
        # Trigger the asynchronous search via Celery
        process_search_order_task.delay(order.id)
    return {"status": "success"}
