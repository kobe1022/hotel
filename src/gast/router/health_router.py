"""HealthRouter."""

from typing import Final

from fastapi import APIRouter

__all__ = ["router"]

router: Final = APIRouter(tags=["Health"])


@router.get("/liveness")
def liveness() -> dict[str, str]:
    """Überprüfen der Liveness.

    :return: JSON-Datensatz mit der Statusmeldung
    :rtype: dict[str, Any]
    """
    return {"status": "up"}
