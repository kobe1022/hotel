"""Fixture für pytest: Neuladen der Datenbank."""

import pytest
from common_api_test import (
    check_readiness,
    db_populate,
    keycloak_populate,
)

# Erläuterung der Fixtures in tests\test\conftest.py


session_scope = "session"


@pytest.fixture(scope=session_scope, autouse=True)
def check_readiness_per_session() -> None:
    check_readiness()
    # Ausgabe in report.html im Wurzelverzeichnis des Projekts
    print("Appserver ist 'ready'")


@pytest.fixture(scope=session_scope, autouse=True)
def populate_per_session() -> None:
    """Fixture, um die DB und Keycloak neu zu laden."""
    db_populate()
    print("DB ist neu geladen")
    keycloak_populate()
    print("Keycloak ist neu geladen")
