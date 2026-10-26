"""Geschäftslogik zum Lesen von Gastdaten."""

from datetime import datetime
from typing import Final
from zoneinfo import ZoneInfo
lazy from collections.abc import Sequence

from loguru import logger
from openpyxl import Workbook

from gast.config import excel_enabled
from gast.repository import (
    GastRepository,
    GastSuchparameter,
    Pageable,
    Session,
    Slice,
)
from gast.security import Role, User
from gast.service.exceptions import ForbiddenError, NotFoundError
from gast.service.gast_dto import GastDTO

__all__ = ["GastService"]


class GastService:
    """Service-Klasse mit Geschäftslogik für Gast."""

    def __init__(self, repo: GastRepository) -> None:
        """Konstruktor mit abhängigem GastRepository."""
        self.repo: GastRepository = repo

    def find_by_id(self, gast_id: int, user: User) -> GastDTO:
        """Suche mit der Gast-ID.

        :param gast_id: ID für die Suche
        :param user: User aus dem Token
        :return: Der gefundene Gast
        :rtype: GastDTO
        :raises NotFoundError: Falls kein Gast gefunden
        :raises ForbiddenError: Falls die Gastdaten nicht gelesen werden dürfen
        """
        logger.debug("gast_id={}, user={}", gast_id, user)

        # Session-Objekt ist die Schnittstelle zur DB, nutzt intern ein Transaktionsobj.
        # implizites "autobegin()" bei einem with-Block
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#auto-begin
        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (gast := self.repo.find_by_id(session=session, gast_id=gast_id)) is None:
                if user_is_admin:
                    message: Final = f"Kein Gast mit der ID {gast_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(gast_id=gast_id)
                logger.debug("nicht admin")
                raise ForbiddenError

            if gast.username != user.username and not user_is_admin:
                logger.debug(
                    "gast.username={}, user.username={}, user.roles={}",
                    gast.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            gast_dto: Final = GastDTO.from_gast(gast)
            session.commit()

        logger.debug("{}", gast_dto)
        return gast_dto

    # ab Python 3.9 (2019) ist der Element-Type in eckigen Klammern und
    # der Name von eingebauten Collections ist kleingeschrieben.
    def find(
        self,
        suchparameter: GastSuchparameter | None,
        pageable: Pageable,
    ) -> Slice[GastDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :return: Liste der gefundenen Gäste
        :rtype: Slice[GastDTO]
        :raises NotFoundError: Falls keine Gäste gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            gast_slice: Final = self.repo.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )
            if len(gast_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            gaeste_dto: Final = tuple(
                GastDTO.from_gast(gast) for gast in gast_slice.content
            )
            session.commit()

        if excel_enabled:
            self._create_excelsheet(gaeste_dto)
        gaeste_dto_slice = Slice(
            content=gaeste_dto,
            total_elements=gast_slice.total_elements,
        )
        logger.debug("{}", gaeste_dto_slice)
        return gaeste_dto_slice

    def find_nachnamen(self, teil: str) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Nachnamen
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: list[str]
        :raises NotFoundError: Falls keine Nachnamen gefunden wurden
        """
        logger.debug("teil={}", teil)
        with Session() as session:
            nachnamen: Final = self.repo.find_nachnamen(teil=teil, session=session)
            session.commit()

        logger.debug("{}", nachnamen)
        if len(nachnamen) == 0:
            raise NotFoundError
        return nachnamen

    def _create_excelsheet(self, gaeste: tuple[GastDTO, ...]) -> None:
        """Ein Excelsheet mit den gefundenen Gästen erstellen.

        :param gaeste: Gästedaten für das Excelsheet
        """
        # https://automatetheboringstuff.com/2e/chapter13
        workbook: Final = Workbook()
        worksheet: Final = workbook.active
        if worksheet is None:
            return

        worksheet.append(["Vorname", "Nachname", "Emailadresse", "Treuestufe"])
        for gast in gaeste:
            worksheet.append((
                gast.vorname,
                gast.nachname,
                gast.email,
                gast.treuestufe,
            ))

        timestamp: Final = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime(
            format="%Y-%m-%d_%H%M%S",
        )
        workbook.save(f"gaeste-{timestamp}.xlsx")
