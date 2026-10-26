"""REST-Schnittstelle für Shutdown."""

import os
import signal
from typing import Any, Final

from fastapi import APIRouter, Depends
from loguru import logger

from gast.security.role import Role
from gast.security.roles_required import RolesRequired

__all__ = ["router"]


router: Final = APIRouter(tags=["Admin"])


# "Dependency Injection" durch Depends
@router.api_route(
    path="/shutdown",
    methods=["QUERY"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def shutdown() -> dict[str, Any]:
    """Der Server wird heruntergefahren."""
    logger.warning("Server shutting down without calling cleanup handlers.")
    # https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c#answer-69812984
    # https://github.com/pallets/werkzeug/issues/1752
    # https://docs.python.org/3/library/os.html#os._exit
    # https://docs.python.org/3/library/sys.html#sys.exit
    # sys.exit(0)  # NOSONAR
    # os._exit(0)
    os.kill(os.getpid(), signal.SIGINT)  # NOSONAR
    return {"message": "Server is shutting down..."}
