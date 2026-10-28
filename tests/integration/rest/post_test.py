"""Tests für POST."""

from http import HTTPStatus
from re import search
from typing import Final

import pytest
from common_api_test import certificate_path, rest_url, timeout
from requests import post

token: str | None


@pytest.mark.rest
@pytest.mark.post_request
@pytest.mark.post_request_success
def test_post() -> None:
    # arrange
    neuer_gast: Final = {
        "vorname": "Vornamerest",
        "nachname": "Nachnamerest",
        "email": "testrest@rest.de",
        "treuestufe": 1,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://rest.de",
        "adresse": {"plz": "99999", "ort": "Restort"},
        "buchungen": [
            {
                "betrag": "999.99",
                "waehrung": "EUR",
                "zimmerkategorie": "DZ",
                "verpflegung": "F",
                "zahlungsart": "K",
                "anreise": "2026-01-10",
                "abreise": "2026-01-12",
                "anzahl_gaeste": 2,
            },
        ],
        "username": "testrest",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    int_pattern: Final = "/[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid() -> None:
    # arrange
    neuer_gast_invalid: Final = {
        "vorname": "Vornamerest",
        "nachname": "falscher_nachname",
        "email": "falsche_email@",
        "treuestufe": 11,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://?!",
        "adresse": {"plz": "1234", "ort": "Restort"},
        "buchungen": [
            {
                "betrag": "222.2",
                "waehrung": "EUR",
                "zimmerkategorie": "DZ",
                "verpflegung": "F",
                "zahlungsart": "K",
                "anreise": "2026-01-10",
                "abreise": "2026-01-12",
                "anzahl_gaeste": 2,
            },
        ],
        "username": "testrestinvalid",
    }
    headers = {"Content-Type": "application/json"}

    # act
    try:
        response: Final = post(
            rest_url,
            json=neuer_gast_invalid,
            headers=headers,
            timeout=timeout,
            verify=certificate_path,
        )
    except BaseException as exc:
        raise RuntimeError("Fehler bei POST") from exc

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "nachname" in body
    assert "email" in body
    assert "treuestufe" in body
    assert "homepage" in body
    assert "plz" in body


@pytest.mark.rest
@pytest.mark.post_request
@pytest.mark.parametrize(
    ("aenderung", "feld"),
    [
        ({"username": "ab"}, "username"),
        ({"geburtsdatum": "2999-01-01"}, "geburtsdatum"),
        ({"buchungen": [{"betrag": "99999999999.99"}]}, "betrag"),
        ({"buchungen": [{"betrag": "-1"}]}, "betrag"),
        ({"buchungen": [{"betrag": "1.234"}]}, "betrag"),
        (
            {"buchungen": [{"anreise": "2026-01-12", "abreise": "2026-01-10"}]},
            "abreise",
        ),
        (
            {"buchungen": [{"anreise": "2026-01-10", "abreise": "2026-01-10"}]},
            "abreise",
        ),
    ],
)
def test_post_verletzt_db_constraints(aenderung: dict, feld: str) -> None:
    """Werte, die die Constraints der DB verletzen, ergeben 422 statt 500."""
    # arrange
    buchung: Final = {
        "betrag": "999.99",
        "waehrung": "EUR",
        "zimmerkategorie": "DZ",
        "verpflegung": "F",
        "zahlungsart": "K",
        "anreise": "2026-01-10",
        "abreise": "2026-01-12",
        "anzahl_gaeste": 2,
    }
    neuer_gast: Final = {
        "vorname": "Vornamerest",
        "nachname": "Nachnamerest",
        "email": "constraints@rest.de",
        "treuestufe": 1,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://rest.de",
        "adresse": {"plz": "99999", "ort": "Restort"},
        "buchungen": [buchung],
        "username": "testconstraints",
    }
    for key, value in aenderung.items():
        if key == "buchungen":
            neuer_gast[key] = [{**buchung, **value[0]}]
        else:
            neuer_gast[key] = value
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert feld in response.text


@pytest.mark.rest
@pytest.mark.post_request
def test_post_email_exists() -> None:
    # arrange
    email_exists: Final = "alice@acme.de"
    neuer_gast: Final = {
        "vorname": "Vornamerest",
        "nachname": "Nachnamerest",
        "email": email_exists,
        "treuestufe": 1,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://rest.de",
        "adresse": {"plz": "99999", "ort": "Restort"},
        "buchungen": [
            {
                "betrag": "999.99",
                "waehrung": "EUR",
                "zimmerkategorie": "DZ",
                "verpflegung": "F",
                "zahlungsart": "K",
                "anreise": "2026-01-10",
                "abreise": "2026-01-12",
                "anzahl_gaeste": 2,
            },
        ],
        "username": "emailexists",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"nachname" "Nachname"}'
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
