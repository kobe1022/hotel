"""Modul für persistente Gastdaten."""

from gast.entity.adresse import Adresse
from gast.entity.base import Base
from gast.entity.buchung import Buchung
from gast.entity.gast import Gast
from gast.entity.verpflegung import Verpflegung
from gast.entity.zahlungsart import Zahlungsart
from gast.entity.zimmerkategorie import Zimmerkategorie

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Adresse",
    "Base",
    "Buchung",
    "Gast",
    "Verpflegung",
    "Zahlungsart",
    "Zimmerkategorie",
]
