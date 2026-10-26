"""Tests für Login."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import (
    base_url,
    certificate_path,
    login,
    timeout,
    token_path,
    username_admin,
)
from requests import request


@pytest.mark.login
def test_login_admin() -> None:
    # act
    token: Final = login()

    # then
    assert isinstance(token, str)
    assert token


@pytest.mark.login
def test_login_falsches_passwort() -> None:
    # arrange
    login_data: Final = {"username": username_admin, "password": "FALSCHES_PASSWORT"}

    # act
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.login
def test_login_ohne_daten() -> None:
    # arrange
    login_data: dict[str, str] = {}

    # act
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED
