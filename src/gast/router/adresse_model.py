"""Pydantic-Model für die Adresse."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from gast.entity import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    """Pydantic-Model für die Adresse."""

    plz: Annotated[str, StringConstraints(pattern=r"^\d{5}$")]
    """Postleitzahl"""
    ort: Annotated[str, StringConstraints(max_length=64)]
    """Ort"""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "plz": "99999",
                "ort": "Testort",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_adresse(self) -> Adresse:
        """Konvertierung in ein Adresse-Objekt für SQLAlchemy.

        :return: Adresse-Objekt für SQLAlchemy
        :rtype: Adresse
        """
        return Adresse(
            id=None,
            plz=self.plz,
            ort=self.ort,
            gast_id=None,
            gast=None,
        )
