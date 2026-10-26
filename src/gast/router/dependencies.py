"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from gast.repository.gast_repository import GastRepository
from gast.service.gast_service import GastService
from gast.service.gast_write_service import GastWriteService

__all__ = ["get_gast_service", "get_gast_write_service", "get_repository"]


def get_repository() -> GastRepository:
    """Factory-Funktion für GastRepository.

    :return: Das Repository
    :rtype: GastRepository
    """
    return GastRepository()


def get_gast_service(
    repo: Annotated[GastRepository, Depends(get_repository)],
) -> GastService:
    """Factory-Funktion für GastService."""
    return GastService(repo=repo)


def get_gast_write_service(
    repo: Annotated[GastRepository, Depends(get_repository)],
) -> GastWriteService:
    """Factory-Funktion für GastWriteService."""
    return GastWriteService(repo=repo)
