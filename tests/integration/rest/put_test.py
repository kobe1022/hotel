"""Tests für PUT."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import put

EMAIL_UPDATE: Final = "alice@acme.de.put"
HOMEPAGE_UPDATE: Final = "https://www.acme.ch.put"


@pytest.mark.rest
@pytest.mark.put_request
def test_put() -> None:
    # arrange
    gast_id: Final = 40
    if_match: Final = '"0"'
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-09",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_invalid() -> None:
    # arrange
    gast_id: Final = 40
    geaenderter_gast_invalid: Final = {
        "vorname": "Vornameput",
        "nachname": "falscher_nachname_put",
        "email": "falsche_email_put@",
        "treuestufe": 11,
        "has_newsletter": False,
        "geburtsdatum": "2022-02-04",
        "homepage": "https://?!",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast_invalid,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "nachname" in response.text
    assert "email" in response.text
    assert "treuestufe" in response.text
    assert "homepage" in response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    gast_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.put_request
def test_put_email_exists() -> None:
    # arrange
    gast_id: Final = 40
    if_match: Final = '"1"'
    email_exists: Final = "alice@acme.de"
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": email_exists,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-09",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    gast_id: Final = 40
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    gast_id: Final = 40
    if_match: Final = '"-1"'
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    gast_id: Final = 40
    if_match: Final = '"xy"'
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    gast_id: Final = 40
    if_match: Final = "0"
    geaenderter_gast: Final = {
        "vorname": "Vornameput",
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "treuestufe": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{gast_id}",
        json=geaenderter_gast,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
