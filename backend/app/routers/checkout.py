"""
Routes related to payment and checkout sessions.

This router exposes an endpoint to create a Stripe Checkout session for
a given order.  The price can be supplied either via a predefined
Stripe price ID or dynamically using the order's price.  The session
metadata stores the order ID so that the webhook can correlate the
payment with the search order.
"""
import logging
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_session
from ..models import SearchOrder

# Configura o logger para este módulo
logger = logging.getLogger(__name__)


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

    if not settings.stripe_api_key or not settings.stripe_api_key.startswith("sk_"):
        logger.error("A chave da API do Stripe (STRIPE_API_KEY) não está configurada ou é inválida.")
        raise HTTPException(
            status_code=500, detail="A integração com o sistema de pagamento não está configurada."
        )

    logger.info(f"Iniciando a criação de sessão de checkout para o pedido ID: {body.order_id}")
    order = await session.get(SearchOrder, body.order_id)
    if not order:
        logger.warning(f"Falha no checkout: Pedido com ID {body.order_id} não encontrado.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    from ..models import OrderStatus  # imported here to avoid circular import
    if order.status != OrderStatus.PENDING_PAYMENT:
        logger.warning(
            f"Falha no checkout: O pedido {order.id} não está aguardando pagamento (status: {order.status})."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not awaiting payment"
        )

    line_item: dict[str, any]
    # CORREÇÃO: Verificamos se o stripe_price_id existe E se ele parece um ID válido.
    # Se não, usamos a criação de preço dinâmica. Isso evita que comentários
    # ou valores inválidos no .env quebrem a aplicação.
    if settings.stripe_price_id and settings.stripe_price_id.startswith("price_"):
        line_item = {"price": settings.stripe_price_id, "quantity": 1}
        logger.info(f"Usando Price ID fixo do .env: {settings.stripe_price_id}")
    else:
        line_item = {
            "price_data": {
                "currency": "brl",
                "product_data": {"name": f"Busca de Certidão ({order.target_name})"},
                "unit_amount": int(order.order_price * 100),
            },
            "quantity": 1,
        }
        logger.info("Usando 'price_data' para criar preço dinamicamente.")

    try:
        logger.info(f"Criando sessão no Stripe para o pedido {order.id} com o item: {line_item}")
        
        success_url = f"{settings.frontend_base_url}/app/dashboard?payment=success&order_id={order.id}"
        cancel_url = f"{settings.frontend_base_url}/checkout/{order.id}?payment=cancelled"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[line_item],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"order_id": str(order.id)},
        )
        logger.info(f"Sessão do Stripe {checkout_session.id} criada com sucesso para o pedido {order.id}")

    except stripe.error.StripeError as e:
        logger.error(f"Erro da API Stripe para o pedido {order.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao criar sessão Stripe para o pedido {order.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao iniciar o pagamento.")

    order.stripe_session_id = checkout_session.id
    await session.commit()
    return {"id": checkout_session.id, "url": checkout_session.url}