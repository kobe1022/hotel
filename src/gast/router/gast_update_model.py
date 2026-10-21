"""Pydantic-Modell für Gastdaten im Request-Body bei PUT."""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr

from gast.entity import Gast

__all__ = ["GastUpdateModel"]


class GastUpdateModel(BaseModel):
    """Pydantic-Modell für Gastdaten im Request-Body bei PUT.

    Enthält nur die Attribute, die `Gast.set()` tatsächlich übernimmt.
    """

    model_config = ConfigDict(extra="forbid")

    vorname: str
    nachname: str
    email: EmailStr
    treuestufe: int
    has_newsletter: bool
    geburtsdatum: date

    def to_entity(self) -> Gast:
        """GastUpdateModel in ein transientes Gast-Entity für GastWriteService.update() umwandeln."""
        return Gast(
            vorname=self.vorname,
            nachname=self.nachname,
            email=self.email,
            treuestufe=self.treuestufe,
            has_newsletter=self.has_newsletter,
            geburtsdatum=self.geburtsdatum,
            homepage=None,
            username=None,
            id=None,
            adresse=None,
            buchungen=[],
            erzeugt=None,
            aktualisiert=None,
        )
