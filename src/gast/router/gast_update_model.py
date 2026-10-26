"""Pydantic-Model zum Aktualisieren von Gastdaten."""

from typing import Annotated
lazy from datetime import date

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, StringConstraints

from gast.entity import Gast

__all__ = ["GastUpdateModel"]


class GastUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Gastdaten."""

    # https://docs.pydantic.dev/latest/usage/types
    vorname: Annotated[str, StringConstraints(max_length=64)]
    """Der Vorname."""
    nachname: Annotated[
        str,
        StringConstraints(
            pattern="^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß]+)?$",
            max_length=64,
        ),
    ]
    """Der Nachname."""
    email: EmailStr
    """Die eindeutige Emailadresse."""
    treuestufe: Annotated[int, Field(ge=1, le=9)]
    """Die Treuestufe."""
    has_newsletter: bool
    """Angabe, ob der Newsletter abonniert ist."""
    geburtsdatum: date = Field(strict=False)
    """Das Geburtsdatum. Keine strikte Validierung: String in JSON."""
    homepage: HttpUrl | None = None
    """Die optionale URL der Homepage."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "vorname": "Test",
                "nachname": "Test",
                "email": "test@acme.com",
                "treuestufe": 1,
                "has_newsletter": True,
                "geburtsdatum": "2023-01-31",
                "homepage": "https://test.rest",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_gast(self) -> Gast:
        """Konvertierung in ein Gast-Objekt für SQLAlchemy.

        :return: Gast-Objekt für SQLAlchemy ohne Adresse und Buchungen.
        :rtype: Gast
        """
        logger.debug("self={}", self)
        gast = Gast(
            id=None,
            vorname=self.vorname,
            nachname=self.nachname,
            email=self.email,
            treuestufe=self.treuestufe,
            has_newsletter=self.has_newsletter,
            geburtsdatum=self.geburtsdatum,
            # HttpUrl ist ungeeignet fuer SQLAlchemy
            homepage=str(self.homepage) if self.homepage is not None else None,
            adresse=None,
            buchungen=[],
            username=None,
            erzeugt=None,
            aktualisiert=None,
        )
        logger.debug("gast={}", gast)
        return gast
