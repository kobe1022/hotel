"""Modul für die REST-Schnittstelle einschließlich Validierung."""

lazy from collections.abc import Sequence

from gast.router.gast_router import gast_router, get, get_by_id, get_nachnamen
from gast.router.gast_write_router import delete_by_id, gast_write_router, post, put
from gast.router.health_router import liveness, router as health_router
from gast.router.hello_router import router as hello_router
from gast.router.shutdown_router import router as shutdown_router

__all__: Sequence[str] = [
    "delete_by_id",
    "gast_router",
    "gast_write_router",
    "get",
    "get_by_id",
    "get_nachnamen",
    "health_router",
    "hello_router",
    "liveness",
    "post",
    "put",
    "shutdown_router",
]
