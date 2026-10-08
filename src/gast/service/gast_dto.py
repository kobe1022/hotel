"""DTO-Klasse für GastDaten."""

from dataclasses import dataclass
lazy from datetime import date

import strawberry

from gast.service.adresse_dto import AdresseDTO
from gast.service.exceptions import GastRequiredError
lazy from gast.entity import Gast


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Gast")
class GastDTO:
    """DTO-Klasse für GastDaten."""

    vorname: str
    nachname: str
    email: str
    treuestufe: int
    has_newsletter: bool
    geburtsdatum: date
    homepage: str | None
    username: str | None
    adresse: AdresseDTO | None

    @classmethod
    def from_entity(cls, gast: Gast) -> GastDTO:
        """GastDTO aus einem Gast-Entity erstellen."""
        if not gast:
            raise GastRequiredError
        return cls(
            vorname=gast.vorname,
            nachname=gast.nachname,
            email=gast.email,
            treuestufe=gast.treuestufe,
            has_newsletter=gast.has_newsletter,
            geburtsdatum=gast.geburtsdatum,
            homepage=gast.homepage,
            username=gast.username,
            adresse=AdresseDTO.from_entity(gast.adresse) if gast.adresse else None,
        )
