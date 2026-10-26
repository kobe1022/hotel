"""Modul für die Service-Schicht zu Gastdaten."""

from gast.service.adresse_dto import AdresseDTO
from gast.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from gast.service.gast_dto import GastDTO
from gast.service.gast_service import GastService
from gast.service.gast_write_service import GastWriteService
from gast.service.mailer import send_mail

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "AdresseDTO",
    "EmailExistsError",
    "ForbiddenError",
    "GastDTO",
    "GastService",
    "GastWriteService",
    "NotFoundError",
    "UsernameExistsError",
    "VersionOutdatedError",
    "send_mail",
]
