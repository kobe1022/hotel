"""Exceptions für die Service-Schicht."""


class GastRequiredError(ValueError):
    """Wird ausgelöst, wenn kein Gast-Objekt übergeben wurde."""

    def __init__(self) -> None:
        """GastRequiredError mit Standardmeldung erzeugen."""
        super().__init__("Gast is required")


class AdresseRequiredError(ValueError):
    """Wird ausgelöst, wenn kein Adresse-Objekt übergeben wurde."""

    def __init__(self) -> None:
        """AdresseRequiredError mit Standardmeldung erzeugen."""
        super().__init__("Adresse is required")


class NotFoundError(ValueError):
    """Wird ausgelöst, wenn kein Gast mit der gegebenen ID existiert."""

    def __init__(self, gast_id: int | None) -> None:
        """NotFoundError mit der gesuchten ID erzeugen."""
        super().__init__(f"Kein Gast mit der ID {gast_id} gefunden")
        self.gast_id = gast_id


class EmailExistsError(ValueError):
    """Wird ausgelöst, wenn die Emailadresse bereits vergeben ist."""

    def __init__(self, email: str) -> None:
        """EmailExistsError mit der betroffenen Emailadresse erzeugen."""
        super().__init__(f"Die Emailadresse {email} existiert bereits")
        self.email = email


class UsernameExistsError(ValueError):
    """Wird ausgelöst, wenn der Benutzername bereits vergeben ist."""

    def __init__(self, username: str | None) -> None:
        """UsernameExistsError mit dem betroffenen Benutzernamen erzeugen."""
        super().__init__(f"Der Benutzername {username} existiert bereits")
        self.username = username


class VersionOutdatedError(ValueError):
    """Wird ausgelöst, wenn die übergebene Versionsnummer veraltet ist."""

    def __init__(self, gast_id: int | None, version: int) -> None:
        """VersionOutdatedError mit ID und veralteter Versionsnummer erzeugen."""
        super().__init__(
            f"Die Versionsnummer {version} ist veraltet für Gast mit ID {gast_id}",
        )
        self.gast_id = gast_id
        self.version = version
