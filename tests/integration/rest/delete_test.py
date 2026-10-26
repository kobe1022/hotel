"""Tests für DELETE."""

from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import delete


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete() -> None:
    # arrange
    gast_id: Final = 60
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == 204  # ruff: ignore[magic-value-comparison]


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete_not_found() -> None:
    # arrange
    gast_id: Final = 999999
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{gast_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == 204  # ruff: ignore[magic-value-comparison]
