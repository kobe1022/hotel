"""Entity-Klasse für Buchung."""

from typing import override
lazy from datetime import date
lazy from decimal import Decimal

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gast.entity.base import Base
from gast.entity.gast import Gast
lazy from gast.entity.verpflegung import Verpflegung
lazy from gast.entity.zahlungsart import Zahlungsart
lazy from gast.entity.zimmerkategorie import Zimmerkategorie


class Buchung(Base):
    """Entity-Klasse für Buchung."""

    __tablename__ = "buchung"

    # https://docs.python.org/3/library/decimal.html
    # Genauigkeit ("precision"): 28
    betrag: Mapped[Decimal]
    """Der Betrag."""

    waehrung: Mapped[str]
    """Die Währung in Euro."""

    # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-mapped-column-enums
    zimmerkategorie: Mapped[Zimmerkategorie]
    """Die Zimmerkategorie."""

    verpflegung: Mapped[Verpflegung]
    """Die Verpflegung."""

    zahlungsart: Mapped[Zahlungsart]
    """Die Zahlungsart."""

    anreise: Mapped[date]
    """Das Anreisedatum."""

    abreise: Mapped[date]
    """Das Abreisedatum."""

    anzahl_gaeste: Mapped[int]
    """Die Anzahl der Gäste."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    gast_id: Mapped[int | None] = mapped_column(ForeignKey("gast.id"))
    """ID des zugehörigen Gastes als Fremdschlüssel in der DB-Tabelle."""

    gast: Mapped[Gast | None] = relationship(back_populates=Gast.buchungen)
    """Das zugehörige transiente Gast-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    @override
    def __repr__(self) -> str:
        """Ausgabe der Buchung als String ohne die Gastdaten."""
        return (
            f"Buchung(id={self.id}, betrag={self.betrag}, waehrung={self.waehrung}, "
            f"zimmerkategorie={self.zimmerkategorie}, verpflegung={self.verpflegung}, "
            f"zahlungsart={self.zahlungsart}, anreise={self.anreise}, "
            f"abreise={self.abreise}, anzahl_gaeste={self.anzahl_gaeste})"
        )
