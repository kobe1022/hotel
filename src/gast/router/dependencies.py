"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from gast.repository.gast_repository import GastRepository
from gast.security.dependencies import get_user_service
from gast.service.gast_service import GastService
from gast.service.gast_write_service import GastWriteService
lazy from gast.security.user_service import UserService

__all__ = ["get_service", "get_write_service", "get_repository"]


def get_repository() -> GastRepository:
    """Factory-Funktion für GastRepository.

    :return: Das Repository
    :rtype: GastRepository
    """
    return GastRepository()


def get_service(
    repo: Annotated[GastRepository, Depends(get_repository)],
) -> GastService:
    """Factory-Funktion für GastService."""
    return GastService(repo=repo)


def get_write_service(
    repo: Annotated[GastRepository, Depends(get_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> GastWriteService:
    """Factory-Funktion für GastWriteService."""
    return GastWriteService(repo=repo, user_service=user_service)
