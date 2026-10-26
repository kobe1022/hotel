"""Pydantic-Model für die Gastdaten."""

from typing import Annotated, Final, override

from loguru import logger
from pydantic import ConfigDict, StringConstraints

from gast.router.gast_update_model import GastUpdateModel
lazy from gast.entity import Gast
lazy from gast.router.adresse_model import AdresseModel
lazy from gast.router.buchung_model import BuchungModel

__all__ = ["GastModel"]


class GastModel(GastUpdateModel):
    """Pydantic-Model für die Gastdaten."""

    adresse: AdresseModel
    """Die zugehörige Adresse."""
    buchungen: list[BuchungModel]
    """Die Liste der Buchungen."""
    # https://docs.pydantic.dev/usage/types
    username: Annotated[str, StringConstraints(max_length=20)]
    """Der Benutzername für Login."""

    # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
    # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
    # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @override
    def to_gast(self) -> Gast:
        """Konvertierung in ein Gast-Objekt für SQLAlchemy.

        :return: Gast-Objekt für SQLAlchemy
        :rtype: Gast
        """
        logger.debug("self={}", self)
        gast: Final = super().to_gast()
        gast.adresse = self.adresse.to_adresse()
        gast.buchungen = [
            buchung_model.to_buchung() for buchung_model in self.buchungen
        ]
        gast.username = self.username
        logger.debug("gast={}", gast)
        return gast
