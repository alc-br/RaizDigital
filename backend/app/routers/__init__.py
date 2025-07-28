"""
Expose API routers in a single namespace.

This module imports the individual router modules and makes their
routers available for inclusion in the main application.  Importing
routers here also ensures that the modules are registered with the
FastAPI application when ``app.include_router`` is called.
"""
from . import auth, orders, webhooks, internal  # noqa: F401
