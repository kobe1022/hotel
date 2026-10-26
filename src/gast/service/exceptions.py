"""Exceptions in der Geschäftslogik."""

lazy from gast.repository.gast_suchparameter import GastSuchparameter

__all__ = [
    "AdresseRequiredError",
    "EmailExistsError",
    "ForbiddenError",
    "NotFoundError",
    "UsernameExistsError",
    "VersionOutdatedError",
]


class EmailExistsError(Exception):
    """Exception, falls die Emailadresse bereits existiert."""

    def __init__(self, email: str) -> None:
        """Initialisierung von EmailExistsError mit der Emailadresse.

        :param email: Bereits existierende Emailadresse
        """
        super().__init__(f"Existierende Email: {email}")
        self.email = email


class EmptyUsernameError(ValueError):
    """Exception, falls der Benutzername leer ist."""

    def __init__(self) -> None:
        """Initialisierung von EmptyUsernameError."""
        super().__init__("username ist None oder leer")


class UsernameExistsError(Exception):
    """Exception, falls der Benutzername bereits existiert."""

    def __init__(self, username: str | None) -> None:
        """Initialisierung von UsernameExistsError mit dem Benutzernamen.

        :param username: Bereits existierender Benutzername
        """
        super().__init__(f"Existierender Benutzername: {username}")
        self.username = username


class ForbiddenError(Exception):
    """Exception, falls es der Zugriff nicht erlaubt ist."""


class NotFoundError(Exception):
    """Exception, falls kein Gast gefunden wurde."""

    def __init__(
        self,
        gast_id: int | None = None,
        suchparameter: GastSuchparameter | None = None,
    ) -> None:
        """Initialisierung von NotFoundError mit ID und Suchparameter.

        :param gast_id: Gast-ID, zu der nichts gefunden wurde
        :param suchparameter: Suchparameter, zu denen nichts gefunden wurde
        """
        super().__init__("Not Found")
        self.gast_id = gast_id
        self.suchparameter = suchparameter


class VersionOutdatedError(Exception):
    """Exception, falls die Versionsnummer beim Aktualisieren veraltet ist."""

    def __init__(self, version: int) -> None:
        """Initialisierung von VersionOutdatedError mit veralteter Versionsnummer.

        :param version: Veraltete Versionsnummer
        """
        super().__init__(f"Veraltete Version: {version}")
        self.version = version


class AdresseRequiredError(RuntimeError):
    """Exception, falls eine Adresse im aktuellen Zustand None ist."""

    def __init__(self) -> None:
        """Initialisierung von AdresseRequiredError."""
        super().__init__("Ungueltiger Zustand: Adresse ist None")
