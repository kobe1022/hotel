"""Fixture für pytest: Repository, Gast(Write)Service, KeycloakAdmin, UserService."""

from typing import TYPE_CHECKING

import pytest

from gast.repository import GastRepository
from gast.security import UserService
from gast.service import GastService, GastWriteService

if TYPE_CHECKING:
    from keycloak import KeycloakAdmin
    from pytest_mock import MockerFixture

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


@pytest.fixture
def gast_repository() -> GastRepository:
    """Fixture für GastRepository."""
    return GastRepository()


@pytest.fixture
def gast_service(gast_repository: GastRepository) -> GastService:
    """Fixture für GastService."""
    return GastService(gast_repository)


@pytest.fixture
def keycloak_admin_mock(mocker: MockerFixture) -> KeycloakAdmin:
    """Patching von KeycloakAdmin() innerhalb von UserService."""
    keycloak_admin_cls_mock = mocker.patch(
        "gast.security.user_service.KeycloakAdmin",
    )
    return keycloak_admin_cls_mock.return_value


@pytest.fixture
def user_service(keycloak_admin_mock) -> UserService:
    """Patching von KeycloakAdmin.get_client_id() fuer UserService."""
    uuid_mock = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_client_id.return_value = uuid_mock
    # Patching von keycloak_admin.get_client_roles()
    gast_rolle_mock = {
        "id": uuid_mock,
        "name": "gast",
        "description": "",
        "composite": False,
        "clientRole": True,
        "containerId": uuid_mock,
    }
    keycloak_admin_mock.get_client_roles.return_value = [gast_rolle_mock]
    return UserService()


@pytest.fixture
def gast_write_service(
    gast_repository: GastRepository,
    user_service: UserService,
) -> GastWriteService:
    """Fixture für GastWriteService."""
    return GastWriteService(gast_repository, user_service)
