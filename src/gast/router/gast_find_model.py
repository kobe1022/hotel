"""Pydantic-Modell für Suchparameter und Pagination bei der Gastsuche."""

from pydantic import BaseModel, ConfigDict

from gast.repository import GastSuchparameter, Pageable

__all__ = ["GastFindModel"]


class GastFindModel(BaseModel):
    """Pydantic-Modell für Query-Parameter bei GET /."""

    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    nachname: str | None = None
    page: str | None = None
    size: str | None = None

    def to_suchparameter(self) -> GastSuchparameter | None:
        """GastFindModel in GastSuchparameter umwandeln."""
        if self.email is None and self.nachname is None:
            return None
        return GastSuchparameter(email=self.email, nachname=self.nachname)

    def to_pageable(self) -> Pageable:
        """GastFindModel in Pageable umwandeln."""
        return Pageable.create(number=self.page, size=self.size)
