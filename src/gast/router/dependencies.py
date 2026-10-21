"""Factory-Funktionen für Dependency Injection."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from gast.repository import Session as SessionFactory
from gast.service.gast_service import GastService
from gast.service.gast_write_service import GastWriteService

__all__ = ["get_gast_service", "get_gast_write_service", "get_session"]


def get_session() -> Generator[Session]:
    """Factory-Funktion für eine SQLAlchemy-Session pro Request.

    Committet nach einem erfolgreichen Request, rollt bei einer Exception zurück.
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_gast_service() -> GastService:
    """Factory-Funktion für GastService."""
    return GastService()


def get_gast_write_service() -> GastWriteService:
    """Factory-Funktion für GastWriteService."""
    return GastWriteService()
