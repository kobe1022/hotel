"""Tests für QUERY."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import request

QUERY_METHOD: Final = "QUERY"
QUERY_URL: Final = f"{rest_url}/query"


@pytest.mark.rest
@pytest.mark.query_request
@pytest.mark.parametrize(
    "email", ["admin@acme.com", "jonas.becker@acme.edu", "lena.becker@acme.de"]
)
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = request(
        method=QUERY_METHOD,
        url=QUERY_URL,
        json=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    gast = content[0]
    assert gast is not None
    assert gast.get("email") == email
    assert gast.get("id") is not None


@pytest.mark.rest
@pytest.mark.query_request
@pytest.mark.parametrize("email", ["nicht@vorhanden.com", "joe.doe@acme.de"])
def test_get_by_email_not_found(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = request(
        method=QUERY_METHOD,
        url=QUERY_URL,
        json=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("teil", ["Becker", "n"])
def test_get_by_nachname(teil: str) -> None:
    # arrange
    params = {"nachname": teil}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = request(
        method=QUERY_METHOD,
        url=QUERY_URL,
        json=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    for p in content:
        nachname = p.get("nachname")
        assert nachname is not None
        assert isinstance(nachname, str)
        assert teil.lower() in nachname.lower()
        assert p.get("id") is not None


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("nachname", ["Notfound", "Foo-Bar"])
def test_get_by_nachname_not_found(nachname: str) -> None:
    # arrange
    params = {"nachname": nachname}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = request(
        method=QUERY_METHOD,
        url=QUERY_URL,
        json=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
