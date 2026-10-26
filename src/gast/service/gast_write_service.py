"""Geschäftslogik zum Schreiben von Gastdaten."""

from typing import Final

from loguru import logger

from gast.repository import GastRepository, Session
from gast.security import User, UserService
from gast.service.exceptions import (
    EmailExistsError,
    EmptyUsernameError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from gast.service.gast_dto import GastDTO
lazy from gast.entity import Gast

__all__ = ["GastWriteService"]


class GastWriteService:
    """Service-Klasse mit Geschäftslogik für Gast."""

    def __init__(self, repo: GastRepository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem GastRepository und UserService."""
        self.repo: GastRepository = repo
        self.user_service: UserService = user_service

    def create(self, gast: Gast) -> GastDTO:
        """Einen neuen Gast anlegen.

        :param gast: Der neue Gast ohne ID
        :return: Der neu angelegte Gast mit generierter ID
        :rtype: GastDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "gast={}, adresse={}, buchungen={}",
            gast,
            gast.adresse,
            gast.buchungen,
        )

        username: Final = gast.username
        if username is None:
            raise EmptyUsernameError

        # https://www.keycloak.org/docs-api/latest/rest-api:
        # GET /admin/realms/{realm}/users
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = gast.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=gast.email,
            nachname=gast.nachname,
            vorname=gast.vorname,
            password="p",  # ruff: ignore[hardcoded-password-func-arg] # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            gast_db: Final = self.repo.create(gast=gast, session=session)
            gast_dto: Final = GastDTO.from_gast(gast_db)
            session.commit()

        # TODO User aus Keycloak loeschen, falls die DB-Transaktion fehlschlaegt

        logger.debug("gast_dto={}", gast_dto)
        return gast_dto

    def update(self, gast: Gast, gast_id: int, version: int) -> GastDTO:
        """Daten eines Gastes ändern.

        :param gast: Die neuen Daten
        :param gast_id: ID des zu aktualisierenden Gastes
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Gast
        :rtype: GastDTO
        :raises NotFoundError: Falls der zu aktualisierende Gast nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("gast_id={}, version={}, {}", gast_id, version, gast)

        with Session() as session:
            if (
                gast_db := self.repo.find_by_id(
                    gast_id=gast_id,
                    session=session,
                )
            ) is None:
                raise NotFoundError(gast_id=gast_id)
            if gast_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = gast.email
            if email != gast_db.email and self.repo.exists_email_other_id(
                gast_id=gast_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            gast_db.set(gast)
            if (
                gast_updated := self.repo.update(gast=gast_db, session=session)
            ) is None:
                raise NotFoundError(gast_id=gast_id)
            gast_dto: Final = GastDTO.from_gast(gast_updated)
            logger.debug("{}", gast_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst COMMIT sichtbar
            gast_dto.version += 1
            return gast_dto

    def delete_by_id(self, gast_id: int) -> None:
        """Einen Gast anhand seiner ID löschen.

        :param gast_id: ID des zu löschenden Gastes
        """
        logger.debug("gast_id={}", gast_id)
        with Session() as session:
            self.repo.delete_by_id(gast_id=gast_id, session=session)
            session.commit()
