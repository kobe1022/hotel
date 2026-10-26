"""REST-Schnittstelle für lesende Zugriffe auf Gastdaten."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Request, Response, status

from gast.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from gast.router.dependencies import get_service
from gast.router.gast_find_model import GastFindModel
from gast.security import Role, RolesRequired, User
from gast.service import GastDTO, GastService

__all__ = ["gast_router"]


gast_router: Final = APIRouter(tags=["Lesen"])

_READ_ROLES: Final = [Role.ADMIN, Role.GAST]


@gast_router.get(
    path="/",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get(
    suchparameter: Annotated[GastFindModel, Query()],
    response: Response,
    service: Annotated[GastService, Depends(get_service)],
) -> list[GastDTO]:
    """Gäste anhand von Suchparametern mit Pagination suchen.

    :param suchparameter: Query-Parameter email/nachname/page/size
    :param response: Response-Objekt, um die Gesamtanzahl im Header mitzugeben
    :param service: Injizierter GastService
    :return: Liste der gefundenen Gäste
    """
    gast_slice = service.find(
        suchparameter=suchparameter.to_suchparameter(),
        pageable=suchparameter.to_pageable(),
    )
    response.headers["X-Total-Count"] = str(gast_slice.total_elements)
    return list(gast_slice.content)


@gast_router.get(
    path="/nachnamen",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get_nachnamen(
    teil: str,
    service: Annotated[GastService, Depends(get_service)],
) -> list[str]:
    """Nachnamen zu einem Teilstring suchen, z.B. für Autocomplete.

    :param teil: Teilstring des gesuchten Nachnamens
    :param service: Injizierter GastService
    :return: Liste der gefundenen Nachnamen
    """
    return list(service.find_nachnamen(teil=teil))


@gast_router.get(
    path="/{gast_id}",
    dependencies=[Depends(RolesRequired(_READ_ROLES))],
    response_model=GastDTO,
)
def get_by_id(
    gast_id: int,
    request: Request,
    response: Response,
    service: Annotated[GastService, Depends(get_service)],
) -> GastDTO | Response:
    """Einen Gast anhand seiner ID suchen.

    :param gast_id: Die ID des gesuchten Gastes
    :param request: Request-Objekt, um den If-None-Match-Header auszuwerten
    :param response: Response-Objekt, um den ETag-Header zu setzen
    :param service: Injizierter GastService
    :return: 200 mit Gastdaten und ETag, 304 falls unverändert
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    gast_dto = service.find_by_id(gast_id=gast_id, user=user)

    etag = f'"{gast_dto.version}"'
    if_none_match = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match == etag
    ):
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    response.headers[ETAG] = etag
    return gast_dto
