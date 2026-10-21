"""REST-Schnittstelle für lesende Zugriffe auf Gastdaten."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from gast.problem_details import ProblemDetails
from gast.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from gast.router.dependencies import get_gast_service, get_session
from gast.router.gast_find_model import GastFindModel
from gast.security import Role, RolesRequired
from gast.service import GastDTO, GastService, NotFoundError

__all__ = ["router"]


router: Final = APIRouter(tags=["Lesen"])

_READ_ROLES: Final = [Role.ADMIN, Role.GAST]


@router.get(
    path="/",
    dependencies=[Depends(RolesRequired(_READ_ROLES))],
)
def find(
    suchparameter: Annotated[GastFindModel, Query()],
    response: Response,
    service: Annotated[GastService, Depends(get_gast_service)],
    session: Annotated[Session, Depends(get_session)],
) -> list[GastDTO]:
    """Gäste anhand von Suchparametern mit Pagination suchen.

    :param suchparameter: Query-Parameter email/nachname/page/size
    :param response: Response-Objekt, um die Gesamtanzahl im Header mitzugeben
    :param service: Injizierter GastService
    :param session: Injizierte SQLAlchemy-Session
    :return: Liste der gefundenen Gäste
    """
    gast_slice = service.find(
        suchparameter=suchparameter.to_suchparameter(),
        pageable=suchparameter.to_pageable(),
        session=session,
    )
    response.headers["X-Total-Count"] = str(gast_slice.total_elements)
    return list(gast_slice.content)


@router.get(
    path="/nachnamen",
    dependencies=[Depends(RolesRequired(_READ_ROLES))],
)
def find_nachnamen(
    teil: str,
    service: Annotated[GastService, Depends(get_gast_service)],
    session: Annotated[Session, Depends(get_session)],
) -> list[str]:
    """Nachnamen zu einem Teilstring suchen, z.B. für Autocomplete.

    :param teil: Teilstring des gesuchten Nachnamens
    :param service: Injizierter GastService
    :param session: Injizierte SQLAlchemy-Session
    :return: Liste der gefundenen Nachnamen
    """
    return list(service.find_nachnamen(teil=teil, session=session))


@router.get(
    path="/{id}",
    dependencies=[Depends(RolesRequired(_READ_ROLES))],
    response_model=GastDTO,
)
def get_by_id(
    id: int,
    request: Request,
    response: Response,
    service: Annotated[GastService, Depends(get_gast_service)],
    session: Annotated[Session, Depends(get_session)],
) -> GastDTO | Response:
    """Einen Gast anhand seiner ID suchen.

    :param id: Die ID des gesuchten Gastes
    :param request: Request-Objekt, um den If-None-Match-Header auszuwerten
    :param response: Response-Objekt, um den ETag-Header zu setzen
    :param service: Injizierter GastService
    :param session: Injizierte SQLAlchemy-Session
    :return: 200 mit Gastdaten und ETag, 304 falls unverändert, 404 falls nicht gefunden
    """
    try:
        gast_dto = service.find_by_id(gast_id=id, session=session)
    except NotFoundError:
        return ProblemDetails.create(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kein Gast mit der ID {id} gefunden",
        ).to_response()

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
