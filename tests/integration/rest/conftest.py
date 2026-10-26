"""Fixture für pytest: Neuladen der Datenbank."""

import pytest
from common_api_test import (
    check_readiness,
    db_populate,
    keycloak_populate,
)

# "Fixtures" sind Funktionen, die vor den Test-Funktionen ausgefuehrt werden, um z.B.
# wiederholt benoetigte Daten bereitzustellen (URLs, DB-Verbindungen usw.).
# Vgl.: @BeforeEach und @BeforeAll bei JUnit
# Ein Fixture ist eine Funktion, die i.a. in conftest.py implementiert wird und fuer
# alle Test-Funktionen im gleichen Verzeichnis verwendet werden kann.
# Eine Fixture-Funktion wir dann als erstes Argument an die Test-Funktion übergeben
# oder hat das Argument autouse=True fuer die implizite Uebergabe.
# Jedes Fixture hat einen Scope: function (= default), class, module, package, session.
# Die Reihenfolge ist: session > package > module > class > function (~ BeforeEach).
# module: 1x die Fixture-Funktionen pro Datei mit Test-Funktionen aufrufen
# session: 1x die Fixture-Funktionen in diesem Verzeichnis aufrufen
# session verwendet man fuer aufwaendige Operationen, z.B. Test-DB laden.

# https://docs.pytest.org/en/stable/explanation/fixtures.html
# https://docs.pytest.org/en/stable/how-to/fixtures.html
# Anzeige aller fixtures ausgehend vom Wurzelverzeichnis:   uv run pytest --fixtures


session_scope = "session"


@pytest.fixture(scope=session_scope, autouse=True)
def check_readiness_per_session() -> None:
    check_readiness()
    # Ausgabe in report.html im Wurzelverzeichnis des Projekts
    print("Appserver ist 'ready'")


@pytest.fixture(scope=session_scope, autouse=True)
def populate_per_session() -> None:
    """Fixture, um die DB und Keycloak neu zu laden."""
    # Ausgabe in report.html im Wurzelverzeichnis des Projekts
    db_populate()
    print("DB ist neu geladen")
    keycloak_populate()
    print("Keycloak ist neu geladen")
