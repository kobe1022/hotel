"""Tests für GET mit QUery-Parameter."""

from http import HTTPStatus
from typing import Any, Final

import pytest
from common_api_test import certificate_path, health_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.health
def test_liveness() -> None:
    # act
    response: Final = get(
        f"{health_url}/liveness",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    status: Final[Any | None] = response_body.get("status")
    assert status == "up"


@pytest.mark.rest
@pytest.mark.health
def test_readiness() -> None:
    # act
    response: Final = get(
        f"{health_url}/readiness",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    status: Final[Any | None] = response_body.get("db")
    assert status == "up"
