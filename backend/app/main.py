"""
Entry point for the FastAPI application.

Creates the FastAPI instance, includes routers, sets up CORS (if
necessary) and runs database initialisation on startup.  This file is
the target of the Uvicorn server when the container starts.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .routers import auth, orders, webhooks, internal, checkout, users


def create_app() -> FastAPI:
    """Factory for the FastAPI application."""
    app = FastAPI(title="RaizDigital API")
    # Configure CORS to allow the frontend to talk to the backend
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Include routers
    app.include_router(auth.router)
    app.include_router(orders.router)
    app.include_router(webhooks.router)
    app.include_router(internal.router)
    app.include_router(checkout.router)
    app.include_router(users.router)
    return app


app = create_app()


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the database on application startup."""
    await init_db()
