"""Tests für Mutations mit GraphQL."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, graphql_url, timeout
from requests import post


@pytest.mark.graphql
@pytest.mark.mutation
def test_create() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    gastInput: {
                        vorname: "Vornamegraphql"
                        nachname: "Nachnamegraphql"
                        email: "testgraphql@graphql.de"
                        treuestufe: 1
                        hasNewsletter: true
                        geburtsdatum: "2022-01-31"
                        homepage: "https://graphql.de"
                        adresse: {
                            plz: "99999"
                            ort: "Mutationort"
                        }
                        buchungen: [
                            {
                                betrag: "999.99"
                                waehrung: "EUR"
                                zimmerkategorie: DOPPELZIMMER
                                verpflegung: FRUEHSTUECK
                                zahlungsart: KREDITKARTE
                                anreise: "2026-01-10"
                                abreise: "2026-01-12"
                                anzahlGaeste: 2
                            }
                        ]
                        username: "testgraphql"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response is not None
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert isinstance(response_body["data"]["create"]["id"], int)
    assert response_body.get("errors") is None


@pytest.mark.graphql
@pytest.mark.mutation
def test_create_invalid() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    gastInput: {
                        vorname: "Vornamegraphql"
                        nachname: "falscher_nachname"
                        email: "falsche_email@"
                        treuestufe: 1
                        hasNewsletter: true
                        geburtsdatum: "2022-01-31"
                        homepage: "https://?!"
                        adresse: {
                            plz: "1234"
                            ort: "Testort"
                        }
                        buchungen: [{
                            betrag: "1"
                            waehrung: "EU"
                            zimmerkategorie: DOPPELZIMMER
                            verpflegung: FRUEHSTUECK
                            zahlungsart: KREDITKARTE
                            anreise: "2026-01-10"
                            abreise: "2026-01-12"
                            anzahlGaeste: 2
                        }]
                        username: "testgraphql"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(
        graphql_url,
        json=query,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"] is None
    errors: Final = response_body["errors"]
    assert isinstance(errors, list)
    assert len(errors) == 1
