"""Tests für GET mit Pfadparameter für die ID."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


# in pyproject.toml bei der Table [tool.pytest.ini_options] gibt es das Array "markers"
@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [30, 1, 20])
def test_get_by_id_admin(gast_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == gast_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [0, 999999])
def test_get_by_id_not_found(gast_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_gast() -> None:
    # arrange
    gast_id: Final = 20
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    gast_id_response: Final = response_body.get("id")
    assert gast_id_response is not None
    assert gast_id_response == gast_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [1, 30])
def test_get_by_id_not_allowed(gast_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [0, 999999])
def test_get_by_id_not_allowed_not_found(gast_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [30, 1, 20])
def test_get_by_id_ungueltiger_token(gast_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}XXX"}

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("gast_id", [30, 1, 20])
def test_get_by_id_ohne_token(gast_id: int) -> None:
    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(("gast_id", "if_none_match"), [(20, '"0"'), (30, '"0"')])
def test_get_by_id_etag(gast_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(
    ("gast_id", "if_none_match"),
    [(30, 'xxx"'), (1, "xxx"), (20, "xxx")],
)
def test_get_by_id_etag_invalid(gast_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == gast_id
