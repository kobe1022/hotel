"""Pydantic-Modell für Adressdaten im Request-Body."""

from pydantic import BaseModel, ConfigDict

from gast.entity.adresse import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    """Pydantic-Modell für Adressdaten im Request-Body."""

    model_config = ConfigDict(extra="forbid")

    plz: str
    ort: str

    def to_entity(self) -> Adresse:
        """AdresseModel in ein transientes Adresse-Entity umwandeln."""
        return Adresse(plz=self.plz, ort=self.ort, id=None, gast_id=None, gast=None)
