"""KeycloakPopulateController."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from gast.config.dev.keycloak_populate import (
    KeycloakPopulateService,
    get_keycloak_populate_service,
)
from gast.security import Role, RolesRequired, User

__all__ = ["router"]


router: Final = APIRouter()


# "Dependency Injection" durch Depends
@router.api_route(
    path="/keycloak_populate",
    methods=["QUERY"],
    tags=["Admin"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
async def populate(
    request: Request,
    service: Annotated[KeycloakPopulateService, Depends(get_keycloak_populate_service)],
) -> JSONResponse:
    """Keycloak mit Testdaten durch einen QUERY-Request neu zu laden.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: dict[str, str]
    """
    body: Final = await request.body()
    if len(body) > 0:
        logger.error("Kein leerer Request-Body")
        return JSONResponse(content="", status_code=status.HTTP_400_BAD_REQUEST)

    current_user: Final[User] = request.state.current_user
    logger.warning(
        'REST-Schnittstelle zum Neuladen von Keycloak aufgerufen von "{}"',
        current_user.username,
    )
    service.populate()
    return JSONResponse(content={"keycloak_populate": "success"})
