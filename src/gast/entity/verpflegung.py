"""Enum für die Verpflegung."""

from enum import StrEnum

import strawberry


# StrEnum ab Python 3.11 (2022), abgeleitet von str
# zusaetzlich als enum fuer das GraphQL-Schema
@strawberry.enum
class Verpflegung(StrEnum):
    """Enum für die Verpflegung."""

    UEBERNACHTUNG = "U"
    """Nur Übernachtung."""

    FRUEHSTUECK = "F"
    """Übernachtung mit Frühstück."""

    HALBPENSION = "HP"
    """Halbpension."""

    VOLLPENSION = "VP"
    """Vollpension."""

    ALL_INCLUSIVE = "AI"
    """All inclusive."""
