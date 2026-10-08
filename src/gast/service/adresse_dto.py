"""DTO for address information."""

from dataclasses import dataclass

import strawberry

from gast.service.exceptions import AdresseRequiredError
lazy from gast.entity import Adresse


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Adresse")
class AdresseDTO:
    """DTO for address information."""

    plz: str
    ort: str

    @classmethod
    def from_entity(cls, adresse: Adresse) -> AdresseDTO:
        """Create an AdresseDTO from an Adresse entity."""
        if not adresse:
            raise AdresseRequiredError
        return cls(
            plz=adresse.plz,
            ort=adresse.ort,
        )
