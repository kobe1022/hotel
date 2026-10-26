"""GastGetRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from gast.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from gast.router.dependencies import get_service
from gast.router.gast_find_model import (
    GastFindModel,
    GastPageModel,
    GastResponseModel,
)
from gast.security import Role, RolesRequired, User
lazy from gast.service import GastService

__all__ = ["gast_router"]


# APIRouter auf Basis der Klasse Router von Starlette
gast_router: Final = APIRouter(tags=["Lesen"])


@gast_router.get(
    path="/{gast_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.GAST]))],
    response_model=GastResponseModel,
)
def get_by_id(
    gast_id: int,
    request: Request,
    service: Annotated[GastService, Depends(get_service)],
) -> Response:
    """Suche mit der Gast-ID.

    :param gast_id: ID des gesuchten Gastes als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Gastdatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Gast gefunden wurde
    :raises ForbiddenError: Falls die Gastdaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("gast_id={}, user={}", gast_id, user)

    gast: Final = service.find_by_id(gast_id=gast_id, user=user)
    logger.debug("{}", gast)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == gast.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    gast_model: Final = GastResponseModel.from_dto(gast)
    return JSONResponse(
        content=gast_model.model_dump(mode="json"),
        headers={ETAG: f'"{gast.version}"'},
    )


@gast_router.get(
    path="",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=GastPageModel,
)
def get(
    find_model: Annotated[GastFindModel, Query()],
    service: Annotated[GastService, Depends(get_service)],
) -> GastPageModel:
    """Suche mit Query-Parameter.

    Siehe https://fastapi.tiangolo.com/tutorial/query-params und
    https://fastapi.tiangolo.com/de/tutorial/query-param-models
    :param find_model: Validierte Such- und Pagination-Parameter als Pydantic-Model
    :param service: Injizierter Service für Geschäftslogik
    :return: Eine Seite mit Gast-Daten
    :raises NotFoundError: Falls keine Gäste gefunden wurden
    """
    logger.debug("search={}", find_model)
    result: Final = _find_page(service=service, find_model=find_model)
    logger.debug("result={}", result)
    return result


@gast_router.get(
    path="/nachnamen/{teil}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=list[str],
)
def get_nachnamen(
    teil: str,
    service: Annotated[GastService, Depends(get_service)],
) -> list[str]:
    """Suche Nachnamen zum gegebenen Teilstring.

    :param teil: Teilstring der gefundenen Nachnamen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 200 und gefundenen Nachnamen im Body
    :rtype: Response
    :raises NotFoundError: Falls keine Nachnamen gefunden wurden
    """
    logger.debug("teil={}", teil)
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return list(nachnamen)


def _find_page(
    service: GastService,
    find_model: GastFindModel,
) -> GastPageModel:
    pageable: Final = find_model.to_pageable()
    gast_slice: Final = service.find(
        suchparameter=find_model.to_suchparameter(),
        pageable=pageable,
    )

    gast_models: Final = tuple(
        GastResponseModel.from_dto(gast) for gast in gast_slice.content
    )

    total_pages: Final = (
        (gast_slice.total_elements + pageable.size - 1) // pageable.size
        if pageable.size > 0
        else 1
    )

    return GastPageModel(
        content=gast_models,
        page={
            "size": pageable.size,
            "number": pageable.number,
            "total_elements": gast_slice.total_elements,
            "total_pages": total_pages,
        },
    )
