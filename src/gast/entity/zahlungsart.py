"""Enum für die Zahlungsart."""

from enum import StrEnum

import strawberry


# StrEnum ab Python 3.11 (2022), abgeleitet von str
# zusaetzlich als enum fuer das GraphQL-Schema
@strawberry.enum
class Zahlungsart(StrEnum):
    """Enum für die Zahlungsart."""

    KREDITKARTE = "K"
    """Kreditkarte."""

    BAR = "B"
    """Barzahlung."""

    UEBERWEISUNG = "U"
    """Überweisung."""

    PAYPAL = "P"
    """PayPal."""
