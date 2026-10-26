"""DTO-Klasse für GastDaten."""

from dataclasses import dataclass
lazy from datetime import date

import strawberry

from gast.service.adresse_dto import AdresseDTO
lazy from gast.entity import Gast

__all__ = ["GastDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Gast")
class GastDTO:
    """DTO-Klasse für GastDaten."""

    id: int
    version: int
    vorname: str
    nachname: str
    email: str
    treuestufe: int
    has_newsletter: bool
    geburtsdatum: date
    homepage: str | None
    username: str | None
    adresse: AdresseDTO

    @classmethod
    def from_gast(cls, gast: Gast) -> GastDTO:
        """GastDTO aus einem Gast-Entity erstellen."""
        return cls(
            id=gast.id if gast.id is not None else -1,
            version=gast.version,
            vorname=gast.vorname,
            nachname=gast.nachname,
            email=gast.email,
            treuestufe=gast.treuestufe,
            has_newsletter=gast.has_newsletter,
            geburtsdatum=gast.geburtsdatum,
            homepage=gast.homepage,
            username=gast.username if gast.username is not None else "N/A",
            adresse=AdresseDTO.from_adresse(gast.adresse),
        )
