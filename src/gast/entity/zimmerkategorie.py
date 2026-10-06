"""Enum für die Zimmerkategorie."""

from enum import StrEnum

import strawberry


# StrEnum ab Python 3.11 (2022), abgeleitet von str
# zusaetzlich als enum fuer das GraphQL-Schema
@strawberry.enum
class Zimmerkategorie(StrEnum):
    """Enum für die Zimmerkategorie."""

    EINZELZIMMER = "EZ"
    """Einzelzimmer."""

    DOPPELZIMMER = "DZ"
    """Doppelzimmer."""

    FAMILIENZIMMER = "FZ"
    """Familienzimmer."""

    JUNIOR_SUITE = "JS"
    """Junior-Suite."""

    SUITE = "S"
    """Suite."""

    PRESIDENTIAL_SUITE = "PS"
    """Presidential-Suite."""
