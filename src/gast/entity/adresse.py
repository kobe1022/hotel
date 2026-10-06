"""Entity-Klasse für die Adresse."""

from typing import override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gast.entity.base import Base
from gast.entity.gast import Gast


class Adresse(Base):
    """Entity-Klasse für die Adresse."""

    __tablename__ = "adresse"

    plz: Mapped[str]
    """Die Postleitzahl."""

    ort: Mapped[str]
    """Der Ort."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    gast_id: Mapped[int | None] = mapped_column(ForeignKey("gast.id"))
    """ID des zugehörigen Gastes als Fremdschlüssel in der DB-Tabelle."""

    gast: Mapped[Gast | None] = relationship(back_populates=Gast.adresse)
    """Das zugehörige transiente Gast-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    @override
    def __repr__(self) -> str:
        """Ausgabe einer Adresse als String ohne die Gastdaten."""
        return f"Adresse(id={self.id}, plz={self.plz}, ort={self.ort})"
