"""
Celery tasks for asynchronous search processing.

This module defines a Celery task that orchestrates the execution of
search robots for a given order.  After the searches are completed it
updates the order status accordingly.  The task is defined as a
regular synchronous function but uses ``asyncio`` internally to call
asynchronous database operations and robot routines.
"""
import asyncio
from datetime import datetime

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import async_session_maker
from .models import OrderStatus, ResultStatus, SearchOrder
from .robots.search_robot import run_search
from .tasks_utils import send_email_task


settings = get_settings()

celery_app = Celery(
    "raizdigital",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="process_search_order_task")
def process_search_order_task(order_id: int) -> None:
    """Entry point for the Celery worker.

    This wrapper makes it possible to run asynchronous code inside a
    synchronous Celery task by scheduling it on an event loop.
    """
    asyncio.run(_process_search_order(order_id))


async def _process_search_order(order_id: int) -> None:
    """Perform the actual processing of a search order asynchronously."""
    async with async_session_maker() as session:
        order: SearchOrder | None = await session.get(SearchOrder, order_id)
        if not order:
            return
        # Perform searches using the robot
        results = await run_search(order)
        # Determine final status
        has_found = any(res.status == ResultStatus.FOUND for res in results)
        order.status = OrderStatus.COMPLETED_SUCCESS if has_found else OrderStatus.COMPLETED_FAILURE
        order.completed_at = datetime.utcnow()
        await session.commit()

        # Send notification email to user asynchronously via Celery
        subject = "Resultado da sua busca de certidão"
        if has_found:
            body = (
                f"Olá {order.user.full_name or order.user.email},\n\n"
                f"Encontramos a certidão procurada para {order.target_name}. Faça login para ver os detalhes.\n\n"
                "Atenciosamente,\nEquipe RaizDigital"
            )
        else:
            body = (
                f"Olá {order.user.full_name or order.user.email},\n\n"
                f"Infelizmente não encontramos a certidão procurada para {order.target_name}.\n"
                "Confira o relatório de busca no seu painel.\n\n"
                "Atenciosamente,\nEquipe RaizDigital"
            )
        send_email_task.delay(order.user.email, subject, body)
