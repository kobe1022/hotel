"""GastWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from gast.problem_details import ProblemDetails
from gast.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from gast.router.dependencies import get_write_service
from gast.security import Role, RolesRequired
lazy from gast.router.gast_model import GastModel
lazy from gast.router.gast_update_model import GastUpdateModel
lazy from gast.service import GastWriteService

__all__ = ["gast_write_router"]


gast_write_router: Final = APIRouter(tags=["Schreiben"])


@gast_write_router.post("")
def post(
    gast_model: GastModel,
    request: Request,
    service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Gast anzulegen.

    :param gast_model: Gastdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("gast_model={}", gast_model)
    gast_dto: Final = service.create(
        gast=gast_model.to_gast(),
    )
    logger.debug("gast_dto={}", gast_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{gast_dto.id}"},
    )


@gast_write_router.put(
    "/{gast_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.GAST]))],
)
def put(
    gast_id: int,
    gast_update_model: GastUpdateModel,
    request: Request,
    service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Gast zu aktualisieren.

    :param gast_id: ID des zu aktualisierenden Gastes als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein Gast existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "gast_id={}, if_match={}, gast_update_model={}",
        gast_id,
        if_match_value,
        gast_update_model,
    )

    if if_match_value is None:
        return ProblemDetails.create(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        ).to_response()

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        ).to_response()

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        ).to_response()

    gast: Final = gast_update_model.to_gast()
    gast_modified: Final = service.update(
        gast=gast,
        gast_id=gast_id,
        version=version_int,
    )
    logger.debug("gast_modified={}", gast_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{gast_modified.version}"'},
    )


@gast_write_router.delete(
    "/{gast_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.GAST]))],
)
def delete_by_id(
    gast_id: int,
    service: Annotated[GastWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Gast anhand seiner ID zu löschen.

    :param gast_id: ID des zu löschenden Gastes
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("gast_id={}", gast_id)
    service.delete_by_id(gast_id=gast_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
