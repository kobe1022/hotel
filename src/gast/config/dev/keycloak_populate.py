"""Neuladen von Keycloak im Modus DEV."""

from csv import DictReader
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from keycloak import KeycloakConnectionError
from loguru import logger

from gast.config import csv_config
from gast.config.dev_modus import dev_keycloak_populate
from gast.security import Role, User, UserService
from gast.security.dependencies import get_user_service

__all__ = [
    "KeycloakPopulateService",
    "get_keycloak_populate_service",
    "keycloak_populate",
]


class KeycloakPopulateService:
    """Service für das Neuladen von Keycloak im Modus DEV."""

    def __init__(self, user_service: UserService) -> None:
        """Konstruktor mit abhängigem UserService."""
        self.user_service: UserService = user_service

    def populate(self) -> None:
        """User-Daten in Keycloak über die REST-Schnittstelle neu laden."""
        if not dev_keycloak_populate:
            return

        logger.warning(">>> Keycloak wird neu geladen <<<")
        try:
            self._remove_users()
            self._create_users()
            logger.warning(">>> Keycloak wurde neu geladen <<<")
        except KeycloakConnectionError:
            logger.error(">>> Keine Keycloak-Verbindung! Ist Keycloak gestartet? <<<")

    def _remove_users(self) -> None:
        self.user_service.remove_all_users()
        logger.debug("Alle User außer 'admin' geloescht")

    def _create_users(self) -> None:
        logger.debug("Aktuelles Verzeichnis: {}", Path.cwd())
        csv_config_path = Path(csv_config)
        if not csv_config_path.is_file():
            logger.error(f"CSV-Datei {csv_config_path} existiert nicht")
            return
        logger.debug("CSV-Datei: {}", csv_config_path)

        # Spalten über ihre Namen lesen (nicht über Nummern), damit eine geänderte
        # Spaltenreihenfolge in gast.csv nicht zu falschen Benutzern führt
        with csv_config_path.open(encoding="utf-8", newline="") as csv_file:
            for row in DictReader(csv_file, delimiter=";"):
                username = row["username"]
                if not username or username == "admin":
                    continue

                user = User(
                    username=username,
                    email=row["email"],
                    nachname=row["nachname"],
                    vorname=row["vorname"],
                    roles=[Role.GAST],
                    password="p",  # ruff: ignore[hardcoded-password-func-arg] # NOSONAR
                )
                self.user_service.create_user(user=user)
        logger.debug("Alle User zu 'gast.csv' neu angelegt")


def get_keycloak_populate_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KeycloakPopulateService:
    """Factory-Funktion für KeycloakPopulateService."""
    return KeycloakPopulateService(user_service)


def keycloak_populate():
    """Keycloak mit Testdaten neu laden, falls im dev-Modus."""
    if dev_keycloak_populate:
        service = get_keycloak_populate_service(get_user_service())
        service.populate()
