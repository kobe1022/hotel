"""Modul für die REST-Schnittstelle einschließlich Validierung."""

lazy from collections.abc import Sequence

from gast.router.health_router import liveness, readiness, router as health_router
from gast.router.hello_router import router as hello_router

__all__: Sequence[str] = [
    "health_router",
    "hello_router",
    "liveness",
    "readiness",
]
