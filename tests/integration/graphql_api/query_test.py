"""Tests für Queries mit GraphQL."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, graphql_url, login_graphql, timeout
from requests import post

GRAPHQL_PATH: Final = "/graphql"


@pytest.mark.graphql
@pytest.mark.query
def test_query_id() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gast(gastId: "20") {
                    version
                    nachname
                    email
                    treuestufe
                    hasNewsletter
                    geburtsdatum
                    homepage
                    adresse {
                        plz
                        ort
                    }
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    data: Final = response_body["data"]
    assert data is not None
    gast: Final = data["gast"]
    assert isinstance(gast, dict)
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_id_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gast(gastId: "999999") {
                    nachname
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"]["gast"] is None
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_email() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gaeste(suchparameter: {email: "admin@acme.com"}) {
                    id
                    version
                    nachname
                    email
                    treuestufe
                    hasNewsletter
                    geburtsdatum
                    homepage
                    adresse {
                        plz
                        ort
                    }
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    gaeste: Final = response_body["data"]["gaeste"]
    assert isinstance(gaeste, list)
    assert len(gaeste) > 0
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_email_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gaeste(suchparameter: {email: "not.found@acme.com"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    gaeste: Final = response_body["data"]["gaeste"]
    assert isinstance(gaeste, list)
    assert len(gaeste) == 0
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_nachname() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gaeste(suchparameter: {nachname: "Alice"}) {
                    id
                    version
                    nachname
                    email
                    treuestufe
                    hasNewsletter
                    geburtsdatum
                    homepage
                    adresse {
                        plz
                        ort
                    }
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    gaeste: Final = response_body["data"]["gaeste"]
    assert isinstance(gaeste, list)
    assert len(gaeste) > 0
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_nachname_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                gaeste(suchparameter: {nachname: "Nichtvorhanden"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    gaeste: Final = response_body["data"]["gaeste"]
    assert isinstance(gaeste, list)
    assert len(gaeste) == 0
