# ruff: file-ignore[hardcoded-password-func-arg]

"""Unit-Tests für find_by_id() von GastService."""

from dataclasses import asdict
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from gast.entity import Adresse, Gast
from gast.security import Role, User
from gast.service import ForbiddenError, GastDTO, GastService, NotFoundError

timezone = ZoneInfo("Europe/Berlin")


@pytest.fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in gast_service.py
    mocker.patch(
        "gast.service.gast_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id(gast_service, session_mock) -> None:
    # Arrange
    gast_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.ADMIN],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        gast_id=gast_id,
        gast=None,
    )
    gast_mock = Gast(
        id=gast_id,
        email=email,
        vorname="Mock",
        nachname=nachname,
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username=username,
        adresse=adresse_mock,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse_mock.gast = gast_mock
    gast_dto_mock = GastDTO.from_gast(gast_mock)
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = gast_mock

    # Act
    gast_dto = gast_service.find_by_id(gast_id=gast_id, user=user_mock)

    # Assert
    assert asdict(gast_dto) == asdict(gast_dto_mock)


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_found(gast_service: GastService, session_mock) -> None:
    # Arrange
    gast_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[Role.ADMIN],
        password="mockpass",
    )
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(NotFoundError) as err:
        gast_service.find_by_id(gast_id=gast_id, user=user_mock)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.gast_id == gast_id


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    gast_service: GastService,
    session_mock,
) -> None:
    # Arrange
    gast_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[],
        password="mockpass",
    )
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(ForbiddenError) as err:
        gast_service.find_by_id(gast_id=gast_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_admin(gast_service, session_mock) -> None:
    # Arrange
    gast_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.GAST],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        gast_id=gast_id,
        gast=None,
    )
    gast_mock = Gast(
        id=gast_id,
        email=email,
        vorname="Mock",
        nachname=nachname,
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username=username,
        adresse=adresse_mock,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse_mock.gast = gast_mock
    gast_dto_mock = GastDTO.from_gast(gast_mock)
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = gast_mock

    # Act
    gast_dto = gast_service.find_by_id(gast_id=gast_id, user=user_mock)

    # Assert
    assert asdict(gast_dto) == asdict(gast_dto_mock)


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_other(gast_service, session_mock) -> None:
    # Arrange
    gast_id = 1
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username="other",
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.GAST],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        gast_id=gast_id,
        gast=None,
    )
    gast_mock = Gast(
        id=gast_id,
        email=email,
        vorname="Mock",
        nachname=nachname,
        treuestufe=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse_mock,
        buchungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    adresse_mock.gast = gast_mock
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = gast_mock

    # Act
    with pytest.raises(ForbiddenError) as err:
        gast_service.find_by_id(gast_id=gast_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError
