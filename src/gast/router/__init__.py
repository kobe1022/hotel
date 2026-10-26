"""Modul für die REST-Schnittstelle einschließlich Validierung."""

lazy from collections.abc import Sequence

from gast.router.gast_router import router as gast_router
from gast.router.gast_write_router import router as gast_write_router
from gast.router.health_router import liveness, router as health_router
from gast.router.hello_router import router as hello_router
from gast.router.shutdown_router import router as shutdown_router

__all__: Sequence[str] = [
    "gast_router",
    "gast_write_router",
    "health_router",
    "hello_router",
    "liveness",
    "shutdown_router",
]
