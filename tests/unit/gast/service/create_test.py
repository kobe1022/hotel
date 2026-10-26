"""Unit-Tests für find_by_id() von GastService."""

from copy import deepcopy
from datetime import date, datetime
from typing import Final
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from gast.entity import Adresse, Gast
from gast.service import EmailExistsError, UsernameExistsError
from gast.service.exceptions import EmptyUsernameError

timezone = ZoneInfo("Europe/Berlin")


@pytest.fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in gast_write_service.py
    mocker.patch(
        "gast.service.gast_write_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@pytest.mark.unit
@pytest.mark.unit_create
def test_create(gast_write_service, session_mock, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        gast_id=None,
        gast=None,
    )
    gast = Gast(
        id=None,
        email=email,
        vorname="Mock",
        nachname="Mocktest",
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse.gast = gast
    gast_db_mock = deepcopy(gast)
    generierte_id: Final[int] = 1
    gast_db_mock.id = generierte_id
    if gast_db_mock.adresse is not None:
        gast_db_mock.adresse.id = generierte_id

    # Patch fuer KeycloakAdmin.get_user_id() und KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None
    keycloak_admin_mock.get_users.return_value = []

    # session.scalar(select(func.count()).where(Gast.email == email)
    session_mock.scalar.return_value = 0
    session_mock.add.return_value = None

    def flush_side_effect(objects=None):
        for obj in objects or []:
            obj.id = generierte_id  # Emulation: generierter PK in session.flush()

    session_mock.flush.side_effect = flush_side_effect

    # Act
    gast_dto = gast_write_service.create(gast=gast)

    # Assert
    assert gast_dto.id == generierte_id


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_username_none(gast_write_service) -> None:
    # Arrange
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        gast_id=None,
        gast=None,
    )
    gast = Gast(
        id=None,
        email="mock@email.test",
        vorname="Mock",
        nachname="Mocktest",
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username=None,
        adresse=adresse,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse.gast = gast

    # Act
    with pytest.raises(
        expected_exception=EmptyUsernameError,
        match="username ist None oder leer",
    ) as err:
        gast_write_service.create(gast=gast)

    # Assert
    assert err.type is EmptyUsernameError


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_username_exists(gast_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        gast_id=None,
        gast=None,
    )
    gast = Gast(
        id=None,
        email=email,
        vorname="Mock",
        nachname="Mocktest",
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse.gast = gast

    # Patch fuer KeycloakAdmin.get_user_id()
    user_id = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_user_id.return_value = user_id
    keycloak_admin_mock.get_users.return_value = []

    # Act
    with pytest.raises(UsernameExistsError) as err:
        gast_write_service.create(gast=gast)

    # Assert
    assert err.type is UsernameExistsError


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_email_exists(gast_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        gast_id=None,
        gast=None,
    )
    gast = Gast(
        id=None,
        email=email,
        vorname="Mock",
        nachname="Mocktest",
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse.gast = gast

    # Patch fuer KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None  # sonst UsernameExistsError
    keycloak_admin_mock.get_users.return_value = [
        {"id": "12345678-1234-1234-1234-123456789012", "email": email},
    ]

    # Act
    with pytest.raises(EmailExistsError) as err:
        gast_write_service.create(gast=gast)

    # Assert
    assert err.type is EmailExistsError
