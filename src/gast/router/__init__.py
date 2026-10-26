"""Modul für die REST-Schnittstelle einschließlich Validierung."""

lazy from collections.abc import Sequence

from gast.router.gast_router import gast_router, get, get_by_id, get_nachnamen, query
from gast.router.gast_write_router import delete_by_id, gast_write_router, post, put
from gast.router.health_router import liveness, readiness, router as health_router
from gast.router.hello_router import router as hello_router
from gast.router.shutdown_router import router as shutdown_router, shutdown

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
    "query",
    "readiness",
    "shutdown",
    "shutdown_router",
]
