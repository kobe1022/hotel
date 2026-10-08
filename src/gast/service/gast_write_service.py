"""Service-Klasse für schreibende Zugriffe auf Gastdaten."""

from typing import Final

lazy from sqlalchemy.orm import Session

from gast.repository.gast_repository import GastRepository
from gast.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
lazy from gast.entity import Gast

__all__ = ["GastWriteService"]


class GastWriteService:
    """Service-Klasse mit schreibenden Zugriffen auf Gastdaten."""

    def __init__(self) -> None:
        """GastWriteService mit eigenem Repository erzeugen."""
        self._repository: Final = GastRepository()

    def create(self, gast: Gast, session: Session) -> Gast:
        """Lege einen neuen Gast an.

        :param gast: Die Daten des neuen Gastes ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Gast mit generierter ID
        :rtype: Gast
        :raises EmailExistsError: falls die Emailadresse bereits existiert
        :raises UsernameExistsError: falls der Benutzername bereits existiert
        """
        self._check_email_exists(email=gast.email, session=session)
        self._check_username_exists(username=gast.username, session=session)
        return self._repository.create(gast=gast, session=session)

    def update(
        self,
        gast_id: int,
        neuer_gast: Gast,
        version: int,
        session: Session,
    ) -> Gast:
        """Aktualisiere einen Gast.

        :param gast_id: ID des zu aktualisierenden Gastes
        :param neuer_gast: Die neuen Gastdaten
        :param version: Erwartete Versionsnummer für optimistische Synchronisation
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Gast
        :rtype: Gast
        :raises NotFoundError: falls kein Gast mit der ID existiert
        :raises VersionOutdatedError: falls die Versionsnummer veraltet ist
        :raises EmailExistsError: falls die Emailadresse bereits bei einem anderen
            Gast existiert
        """
        gast_db = self._repository.find_by_id(gast_id=gast_id, session=session)
        if gast_db is None:
            raise NotFoundError(gast_id)

        if version != gast_db.version:
            raise VersionOutdatedError(gast_id=gast_id, version=version)

        self._check_email_exists_other_id(
            email=neuer_gast.email,
            gast_id=gast_id,
            session=session,
        )

        gast_db.set(neuer_gast)
        aktualisiert = self._repository.update(gast=gast_db, session=session)
        if aktualisiert is None:
            raise NotFoundError(gast_id)
        return aktualisiert

    def delete_by_id(self, gast_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Gast.

        :param gast_id: Die ID des zu löschenden Gastes
        :param session: Session für SQLAlchemy
        """
        self._repository.delete_by_id(gast_id=gast_id, session=session)

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
