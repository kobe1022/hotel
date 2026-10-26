"""Pydantic-Modelle für das Lesen von Gastdaten."""

from typing import Annotated
lazy from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from gast.repository import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    GastSuchparameter,
    Pageable,
)
lazy from gast.service import GastDTO

__all__ = ["GastFindModel", "GastPageModel", "GastResponseModel"]


class GastFindModel(BaseModel):
    """Suchparameter und Pagination für die Gastsuche."""

    email: str | None = None
    nachname: str | None = None
    page: Annotated[int, Field(ge=DEFAULT_PAGE_NUMBER)] = DEFAULT_PAGE_NUMBER
    size: Annotated[int, Field(ge=0, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE

    # Keine weiteren Attribute erlaubt
    # unveraenderlich
    # https://pydantic.dev/docs/validation/latest/concepts/config
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config
    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_pageable(self) -> Pageable:
        """Erzeugt die Pagination-Daten aus den validierten Parametern."""
        return Pageable(number=self.page, size=self.size)

    def to_suchparameter(self) -> GastSuchparameter:
        """Erzeugt Suchparameter für den Service."""
        return GastSuchparameter(email=self.email, nachname=self.nachname)


class AdresseResponseModel(BaseModel):
    """Adresse als Teil eines Model-Objekts für Gäste als Response.

    Damit beim Konvertieren von `GastDTO` in `GastResponseModel` auch die
    Attribute von `AdresseDTO`übernommen werden, ist `ConfigDict(from_attributes=True)`
    notwendig. Siehe
    https://pydantic.dev/docs/validation/latest/concepts/models/#nested-attributes
    """

    plz: str
    ort: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")


class GastResponseModel(BaseModel):
    """Pydantic-Modell für einen gefundenen Gast.

    FastAPI konvertiert implizit das die Felder in JSON, z.B.
    date als String "2000-01-31".
    """

    id: int
    vorname: str
    nachname: str
    email: str
    treuestufe: int
    has_newsletter: bool
    geburtsdatum: date
    homepage: str | None
    adresse: AdresseResponseModel
    username: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict

    @classmethod
    def from_dto(cls, gast: GastDTO) -> GastResponseModel:
        """Konvertiert ein GastDTO in ein Pydantic-Modell für einen Response.

        Der Aufruf von `model_validate` erfordert die Übernahme der korrespondierende
        Attributwerte aus dem DTO-Objekt. Dafür ist `ConfigDict(from_attributes=True)`
        notwendig.
        Siehe https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances
        Der Aufwand für (unnötige) Validierung ist dabei minimal:
        https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation
        """
        return cls.model_validate(gast)


class PageMetaModel(BaseModel):
    """Metadaten für eine Page mit Gastdaten."""

    size: int
    number: int
    total_elements: int
    total_pages: int


class GastPageModel(BaseModel):
    """Pydantic-Modell für einen Response bei einer Suche mit Pagination."""

    content: tuple[GastResponseModel, ...]
    page: PageMetaModel
