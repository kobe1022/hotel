"""DTO for address information."""

from dataclasses import dataclass

import strawberry

from gast.service.exceptions import AdresseRequiredError
lazy from gast.entity import Adresse

__all__ = ["AdresseDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Adresse")
class AdresseDTO:
    """DTO for address information."""

    plz: str
    ort: str

    @classmethod
    def from_adresse(cls, adresse: Adresse | None) -> AdresseDTO:
        """Create an AdresseDTO from an Adresse entity."""
        if adresse is None:
            raise AdresseRequiredError
        return cls(
            plz=adresse.plz,
            ort=adresse.ort,
        )
