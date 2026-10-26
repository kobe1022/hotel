"""REST-Schnittstelle für schreibende Zugriffe auf Gastdaten."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger
from sqlalchemy.orm import Session

from gast.problem_details import ProblemDetails
from gast.router.constants import IF_MATCH
from gast.router.dependencies import get_gast_write_service, get_session
from gast.router.gast_model import GastModel
from gast.router.gast_update_model import GastUpdateModel
from gast.security import Role, RolesRequired
from gast.service import (
    EmailExistsError,
    GastWriteService,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)

__all__ = ["router"]


router: Final = APIRouter(tags=["Schreiben"])

_WRITE_ROLES: Final = [Role.ADMIN, Role.GAST]


@router.post(
    path="/",
    dependencies=[Depends(RolesRequired(_WRITE_ROLES))],
    status_code=status.HTTP_201_CREATED,
)
def create(
    gast_model: GastModel,
    request: Request,
    write_service: Annotated[GastWriteService, Depends(get_gast_write_service)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Einen neuen Gast anlegen.

    :param gast_model: Die Gastdaten aus dem Request-Body
    :param request: Request-Objekt, um die Location-URL zusammenzubauen
    :param write_service: Injizierter GastWriteService
    :param session: Injizierte SQLAlchemy-Session
    :return: 201 mit Location-Header, 400 falls Email/Username bereits vergeben
    """
    try:
        erzeugt = write_service.create(gast=gast_model.to_entity(), session=session)
    except (EmailExistsError, UsernameExistsError) as err:
        return ProblemDetails.create(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ).to_response()

    location = f"{request.url}{erzeugt.id}"
    logger.debug("location={}", location)
    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": location},
    )


@router.put(
    path="/{id}",
    dependencies=[Depends(RolesRequired(_WRITE_ROLES))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def update(
    id: int,
    gast_update_model: GastUpdateModel,
    request: Request,
    write_service: Annotated[GastWriteService, Depends(get_gast_write_service)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Einen vorhandenen Gast aktualisieren (Optimistic Locking über If-Match).

    :param id: Die ID des zu aktualisierenden Gastes
    :param gast_update_model: Die neuen Gastdaten aus dem Request-Body
    :param request: Request-Objekt, um den If-Match-Header auszuwerten
    :param write_service: Injizierter GastWriteService
    :param session: Injizierte SQLAlchemy-Session
    :return: 204 bei Erfolg, 400/404/412/428 im Fehlerfall
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

    try:
        write_service.update(
            gast_id=id,
            neuer_gast=gast_update_model.to_entity(),
            version=int(version),
            session=session,
        )
    except NotFoundError as err:
        return ProblemDetails.create(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ).to_response()
    except VersionOutdatedError as err:
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(err),
        ).to_response()
    except EmailExistsError as err:
        return ProblemDetails.create(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ).to_response()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/{id}",
    dependencies=[Depends(RolesRequired(_WRITE_ROLES))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_by_id(
    id: int,
    write_service: Annotated[GastWriteService, Depends(get_gast_write_service)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Einen Gast löschen.

    :param id: Die ID des zu löschenden Gastes
    :param write_service: Injizierter GastWriteService
    :param session: Injizierte SQLAlchemy-Session
    :return: 204, auch falls der Gast nicht (mehr) existiert
    """
    write_service.delete_by_id(gast_id=id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
