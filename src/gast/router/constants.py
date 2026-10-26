"""Konstanten für REST-Header beim Optimistic Locking."""

from typing import Final

__all__ = ["ETAG", "IF_MATCH", "IF_NONE_MATCH", "IF_NONE_MATCH_MIN_LEN"]

ETAG: Final = "ETag"
"""Name des Response-Headers mit der aktuellen Versionsnummer."""

IF_MATCH: Final = "If-Match"
"""Name des Request-Headers bei PUT für Optimistic Locking."""

IF_NONE_MATCH: Final = "If-None-Match"
"""Name des Request-Headers bei GET, um ein 304 Not Modified zu ermöglichen."""

# minimal gueltiger Wert ist z.B. '"0"': Anfuehrungszeichen + 1 Ziffer + Anfuehrungszeichen
IF_NONE_MATCH_MIN_LEN: Final = 3
"""Mindestlänge eines gültigen If-None-Match-Headers."""
