"""Service-Klasse für lesende Zugriffe auf Gastdaten."""

from typing import Final
lazy from collections.abc import Sequence

from gast.repository import Session
from gast.repository.slice import Slice
from gast.security import Role, User
from gast.service.exceptions import ForbiddenError, NotFoundError
from gast.service.gast_dto import GastDTO
lazy from gast.repository.gast_repository import GastRepository
lazy from gast.repository.gast_suchparameter import GastSuchparameter
lazy from gast.repository.pageable import Pageable

__all__ = ["GastService"]


class GastService:
    """Service-Klasse mit lesenden Zugriffen auf Gastdaten."""

    def __init__(self, repo: GastRepository) -> None:
        """Konstruktor mit abhängigem GastRepository."""
        self._repository: Final = repo

    def find_by_id(self, gast_id: int, user: User) -> GastDTO:
        """Suche mit der Gast-ID.

        :param gast_id: ID des gesuchten Gastes
        :param user: User aus dem Token
        :return: GastDTO zum gefundenen Gast
        :rtype: GastDTO
        :raises NotFoundError: falls kein Gast mit der ID existiert
        :raises ForbiddenError: falls die Gastdaten nicht gelesen werden dürfen
        """
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            gast = self._repository.find_by_id(gast_id=gast_id, session=session)
            if gast is None:
                if user_is_admin:
                    raise NotFoundError(gast_id)
                raise ForbiddenError

            if gast.username != user.username and not user_is_admin:
                raise ForbiddenError

            return GastDTO.from_entity(gast)

    def find(
        self,
        suchparameter: GastSuchparameter | None,
        pageable: Pageable,
    ) -> Slice[GastDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Anzahl Datensätze und Seitennummer
        :return: Ausschnitt der gefundenen Gäste als GastDTO
        :rtype: Slice[GastDTO]
        """
        with Session() as session:
            gast_slice = self._repository.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )
            return Slice(
                content=tuple(GastDTO.from_entity(gast) for gast in gast_slice.content),
                total_elements=gast_slice.total_elements,
            )

    def find_nachnamen(self, teil: str) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring zu den gesuchten Nachnamen
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: Sequence[str]
        """
        with Session() as session:
            return self._repository.find_nachnamen(teil=teil, session=session)
