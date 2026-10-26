"""Pydantic-Model für die Buchungen."""

from typing import Annotated
lazy from datetime import date
lazy from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from gast.entity import Buchung, Verpflegung, Zahlungsart, Zimmerkategorie

__all__ = ["BuchungModel"]


class BuchungModel(BaseModel):
    """Pydantic-Model für die Buchungen."""

    betrag: Decimal = Field(strict=False)
    """Der Betrag. Keine strikte Validierung: JSON -> float in Python."""
    waehrung: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    """Die Währung."""
    zimmerkategorie: Zimmerkategorie = Field(strict=False)
    """Die Zimmerkategorie. Keine strikte Validierung: String in JSON."""
    verpflegung: Verpflegung = Field(strict=False)
    """Die Verpflegung. Keine strikte Validierung: String in JSON."""
    zahlungsart: Zahlungsart = Field(strict=False)
    """Die Zahlungsart. Keine strikte Validierung: String in JSON."""
    anreise: date = Field(strict=False)
    """Das Anreisedatum. Keine strikte Validierung: String in JSON."""
    abreise: date = Field(strict=False)
    """Das Abreisedatum. Keine strikte Validierung: String in JSON."""
    anzahl_gaeste: Annotated[int, Field(ge=1, le=10)]
    """Die Anzahl der Gäste."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "betrag": "999.99",
                "waehrung": "EUR",
                "zimmerkategorie": "DZ",
                "verpflegung": "F",
                "zahlungsart": "K",
                "anreise": "2026-01-10",
                "abreise": "2026-01-12",
                "anzahl_gaeste": 2,
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_buchung(self) -> Buchung:
        """Konvertierung in ein Buchung-Objekt für SQLAlchemy.

        :return: Buchung-Objekt für SQLAlchemy
        :rtype: Buchung
        """
        return Buchung(
            id=None,
            betrag=self.betrag,
            waehrung=self.waehrung,
            zimmerkategorie=self.zimmerkategorie,
            verpflegung=self.verpflegung,
            zahlungsart=self.zahlungsart,
            anreise=self.anreise,
            abreise=self.abreise,
            anzahl_gaeste=self.anzahl_gaeste,
            gast_id=None,
            gast=None,
        )
