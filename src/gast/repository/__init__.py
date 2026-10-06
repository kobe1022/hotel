"""Modul für den DB-Zugriff."""

from gast.repository.gast_repository import GastRepository
from gast.repository.gast_suchparameter import GastSuchparameter
from gast.repository.pageable import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Pageable,
)
from gast.repository.session_factory import Session, engine
from gast.repository.slice import Slice

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "DEFAULT_PAGE_NUMBER",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "GastRepository",
    "GastSuchparameter",
    "Pageable",
    "Session",
    "Slice",
    "engine",
]
