"""Unit-Tests für find() von GastService."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from gast.entity import Adresse, Gast
from gast.repository import GastSuchparameter, Pageable
from gast.service import NotFoundError

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
@pytest.mark.unit_find
def test_find_by_nachname(gast_service, session_mock) -> None:
    # Arrange
    nachname = "Mocktest"
    gast_id = 1
    adresse_mock = Adresse(
        id=1,
        plz="11111",
        ort="Mockort",
        gast_id=gast_id,
        gast=None,
    )
    gast_mock = Gast(
        id=gast_id,
        email="mock@email.test",
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
    suchparameter = GastSuchparameter(nachname=nachname)
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Gast)...).all()
    session_mock.scalars.return_value.all.return_value = [gast_mock]

    # Act
    gaeste_slice = gast_service.find(
        suchparameter=suchparameter,
        pageable=pageable,
    )

    # Assert
    assert len(gaeste_slice.content) == 1
    assert gaeste_slice.content[0].nachname == nachname


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_nachname_not_found(gast_service, session_mock) -> None:
    # Arrange
    nachname = "Notfound"
    suchparameter = GastSuchparameter(nachname=nachname)
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Gast)...).all()
    session_mock.scalars.return_value.all.return_value = []

    # Act
    with pytest.raises(NotFoundError) as err:
        gast_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.nachname == nachname  # pyright: ignore[reportOptionalMemberAccess]


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_email(gast_service, session_mock) -> None:
    # Arrange
    email = "mock@email.test"
    gast_id = 1
    adresse_mock = Adresse(
        id=1,
        plz="11111",
        ort="Mockort",
        gast_id=gast_id,
        gast=None,
    )
    gast_mock = Gast(
        id=gast_id,
        email=email,
        vorname="Mock",
        nachname="Mocktest",
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
    suchparameter = GastSuchparameter(email=email)
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = gast_mock

    # Act
    gaeste_slice = gast_service.find(
        suchparameter=suchparameter,
        pageable=pageable,
    )

    # Assert
    assert len(gaeste_slice.content) == 1
    assert gaeste_slice.content[0].email == email


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_email_not_found(gast_service, session_mock) -> None:
    # Arrange
    email = "not@found.mock"
    suchparameter = GastSuchparameter(email=email)
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Gast)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(NotFoundError) as err:
        gast_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.email == email  # pyright: ignore[reportOptionalMemberAccess]
