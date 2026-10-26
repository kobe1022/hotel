"""REST-Schnittstelle für schreibende Zugriffe auf Gastdaten."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from gast.problem_details import ProblemDetails
from gast.router.constants import IF_MATCH
from gast.router.dependencies import get_write_service
from gast.router.gast_model import GastModel
from gast.router.gast_update_model import GastUpdateModel
from gast.security import Role, RolesRequired
lazy from gast.service import GastWriteService

__all__ = ["gast_write_router"]


gast_write_router: Final = APIRouter(tags=["Schreiben"])

_WRITE_ROLES: Final = [Role.ADMIN, Role.GAST]


@gast_write_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
)
def post(
    gast_model: GastModel,
    request: Request,
    write_service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """Einen neuen Gast anlegen.

    :param gast_model: Die Gastdaten aus dem Request-Body
    :param request: Request-Objekt, um die Location-URL zusammenzubauen
    :param write_service: Injizierter GastWriteService
    :return: 201 mit Location-Header
    """
    erzeugt = write_service.create(gast=gast_model.to_entity())
    location = f"{request.url}/{erzeugt.id}"
    logger.debug("location={}", location)
    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": location},
    )


@gast_write_router.put(
    path="/{gast_id}",
    dependencies=[Depends(RolesRequired(_WRITE_ROLES))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def put(
    gast_id: int,
    gast_update_model: GastUpdateModel,
    request: Request,
    write_service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """Einen vorhandenen Gast aktualisieren (Optimistic Locking über If-Match).

    :param gast_id: Die ID des zu aktualisierenden Gastes
    :param gast_update_model: Die neuen Gastdaten aus dem Request-Body
    :param request: Request-Objekt, um den If-Match-Header auszuwerten
    :param write_service: Injizierter GastWriteService
    :return: 204 bei Erfolg, 412/428 bei fehlerhaftem If-Match-Header
    """
    if_match = request.headers.get(IF_MATCH)
    if if_match is None:
        return ProblemDetails.create(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Der Header 'If-Match' fehlt.",
        ).to_response()

    version = if_match.replace('"', "")
    if not version.isdigit():
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Der Header 'If-Match' ist ungueltig.",
        ).to_response()

    write_service.update(
        gast=gast_update_model.to_entity(),
        gast_id=gast_id,
        version=int(version),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@gast_write_router.delete(
    path="/{gast_id}",
    dependencies=[Depends(RolesRequired(_WRITE_ROLES))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_by_id(
    gast_id: int,
    write_service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """Einen Gast löschen.

    :param gast_id: Die ID des zu löschenden Gastes
    :param write_service: Injizierter GastWriteService
    :return: 204, auch falls der Gast nicht (mehr) existiert
    """
    write_service.delete_by_id(gast_id=gast_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
