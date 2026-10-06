"""Filter für die Gastsuche."""

from dataclasses import dataclass

__all__ = ["GastSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GastSuchparameter:
    """Suchparameter für die Gastsuche."""

    email: str | None = None
    """Exakte Emailadresse als Suchparameter."""

    nachname: str | None = None
    """Teil des Nachnamens als Suchparameter."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return self.email is None and self.nachname is None
