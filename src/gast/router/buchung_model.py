"""Pydantic-Modell für Buchungsdaten im Request-Body."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from gast.entity.buchung import Buchung
from gast.entity.verpflegung import Verpflegung
from gast.entity.zahlungsart import Zahlungsart
from gast.entity.zimmerkategorie import Zimmerkategorie

__all__ = ["BuchungModel"]


class BuchungModel(BaseModel):
    """Pydantic-Modell für Buchungsdaten im Request-Body."""

    model_config = ConfigDict(extra="forbid")

    betrag: Decimal
    waehrung: str
    zimmerkategorie: Zimmerkategorie
    verpflegung: Verpflegung
    zahlungsart: Zahlungsart
    anreise: date
    abreise: date
    anzahl_gaeste: int

    def to_entity(self) -> Buchung:
        """BuchungModel in ein transientes Buchung-Entity umwandeln."""
        return Buchung(
            betrag=self.betrag,
            waehrung=self.waehrung,
            zimmerkategorie=self.zimmerkategorie,
            verpflegung=self.verpflegung,
            zahlungsart=self.zahlungsart,
            anreise=self.anreise,
            abreise=self.abreise,
            anzahl_gaeste=self.anzahl_gaeste,
            id=None,
            gast_id=None,
            gast=None,
        )
