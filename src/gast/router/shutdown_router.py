"""REST-Schnittstelle zum kontrollierten Herunterfahren des Servers."""

from os import getpid, kill
from signal import SIGTERM
from typing import Final

from fastapi import APIRouter, Depends
from loguru import logger

from gast.security import Role, RolesRequired

__all__ = ["router"]

router: Final = APIRouter(tags=["Admin"])


@router.post(
    path="/",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def shutdown() -> dict[str, str]:
    """Den Server kontrolliert herunterfahren (nur für Admins).

    :return: JSON-Datensatz mit Statusmeldung, bevor der Prozess sich beendet
    """
    logger.warning("Shutdown wurde angefordert")
    kill(getpid(), SIGTERM)
    return {"status": "shutting down"}
