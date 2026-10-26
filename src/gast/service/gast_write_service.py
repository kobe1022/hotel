"""Service-Klasse für schreibende Zugriffe auf Gastdaten."""

from typing import Final

from gast.repository import Session
from gast.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from gast.service.gast_dto import GastDTO
lazy from gast.entity import Gast
lazy from gast.repository.gast_repository import GastRepository

__all__ = ["GastWriteService"]


class GastWriteService:
    """Service-Klasse mit schreibenden Zugriffen auf Gastdaten."""

    def __init__(self, repo: GastRepository) -> None:
        """Konstruktor mit abhängigem GastRepository."""
        self._repository: Final = repo

    def create(self, gast: Gast) -> GastDTO:
        """Lege einen neuen Gast an.

        :param gast: Die Daten des neuen Gastes ohne ID
        :return: Der neu angelegte Gast mit generierter ID
        :rtype: GastDTO
        :raises EmailExistsError: falls die Emailadresse bereits existiert
        :raises UsernameExistsError: falls der Benutzername bereits existiert
        """
        with Session() as session:
            self._check_email_exists(email=gast.email, session=session)
            self._check_username_exists(username=gast.username, session=session)
            gast_db: Final = self._repository.create(gast=gast, session=session)
            gast_dto: Final = GastDTO.from_entity(gast_db)
            session.commit()
        return gast_dto

    def update(self, gast: Gast, gast_id: int, version: int) -> GastDTO:
        """Aktualisiere einen Gast.

        :param gast: Die neuen Gastdaten
        :param gast_id: ID des zu aktualisierenden Gastes
        :param version: Erwartete Versionsnummer für optimistische Synchronisation
        :return: Der aktualisierte Gast
        :rtype: GastDTO
        :raises NotFoundError: falls kein Gast mit der ID existiert
        :raises VersionOutdatedError: falls die Versionsnummer veraltet ist
        :raises EmailExistsError: falls die Emailadresse bereits bei einem anderen
            Gast existiert
        """
        with Session() as session:
            gast_db = self._repository.find_by_id(gast_id=gast_id, session=session)
            if gast_db is None:
                raise NotFoundError(gast_id)

            if version != gast_db.version:
                raise VersionOutdatedError(gast_id=gast_id, version=version)

            self._check_email_exists_other_id(
                email=gast.email,
                gast_id=gast_id,
                session=session,
            )

            gast_db.set(gast)
            aktualisiert = self._repository.update(gast=gast_db, session=session)
            if aktualisiert is None:
                raise NotFoundError(gast_id)
            gast_dto: Final = GastDTO.from_entity(aktualisiert)

            session.commit()
            # CAVEAT: Die erhöhte Versionsnummer ist erst nach dem COMMIT sichtbar
            gast_dto.version += 1
            return gast_dto

    def delete_by_id(self, gast_id: int) -> None:
        """Lösche die Daten zu einem Gast.

        :param gast_id: Die ID des zu löschenden Gastes
        """
        with Session() as session:
            self._repository.delete_by_id(gast_id=gast_id, session=session)
            session.commit()

    def _check_email_exists(self, email: str, session: Session) -> None:
        if self._repository.exists_email(email=email, session=session):
            raise EmailExistsError(email)

    def _check_email_exists_other_id(
        self,
        email: str,
        gast_id: int,
        session: Session,
    ) -> None:
        if self._repository.exists_email_other_id(
            email=email,
            gast_id=gast_id,
            session=session,
        ):
            raise EmailExistsError(email)

    def _check_username_exists(self, username: str | None, session: Session) -> None:
        if self._repository.exists_username(username=username, session=session):
            raise UsernameExistsError(username)
