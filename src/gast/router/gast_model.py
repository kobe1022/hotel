"""Pydantic-Modell für Gastdaten im Request-Body bei POST."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from gast.entity import Gast
from gast.router.adresse_model import AdresseModel
from gast.router.buchung_model import BuchungModel

__all__ = ["GastModel"]


class GastModel(BaseModel):
    """Pydantic-Modell für Gastdaten im Request-Body bei POST."""

    model_config = ConfigDict(extra="forbid")

    vorname: str
    nachname: str
    email: EmailStr
    treuestufe: int
    has_newsletter: bool
    geburtsdatum: date
    homepage: str | None = None
    username: Annotated[str, StringConstraints(max_length=20)]
    adresse: AdresseModel
    buchungen: list[BuchungModel] = Field(default_factory=list)

    def to_entity(self) -> Gast:
        """GastModel in ein transientes Gast-Entity für GastWriteService.create() umwandeln."""
        return Gast(
            vorname=self.vorname,
            nachname=self.nachname,
            email=self.email,
            treuestufe=self.treuestufe,
            has_newsletter=self.has_newsletter,
            geburtsdatum=self.geburtsdatum,
            homepage=self.homepage,
            username=self.username,
            id=None,
            adresse=self.adresse.to_entity(),
            buchungen=[buchung.to_entity() for buchung in self.buchungen],
            erzeugt=None,
            aktualisiert=None,
        )
