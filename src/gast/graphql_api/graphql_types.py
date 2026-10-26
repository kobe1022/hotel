"""Schema für GraphQL."""

lazy from datetime import date
lazy from decimal import Decimal

import strawberry

lazy from gast.entity import (
    Verpflegung,
    Zahlungsart,
    Zimmerkategorie,
)

__all__ = [
    "AdresseInput",
    "BuchungInput",
    "CreatePayload",
    "GastInput",
    "Suchparameter",
]

# SDL (schema definition language):
# type Gast {
#     nachname: String!
# }
# type Query {
#     gast(gast_id: ID!): Gast!
#     gaeste(input: Suchparameter): [Gast!]
# }
# type Mutation {
#     create(gast_input: GastInput!): CreatePayload!
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Gästen."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class AdresseInput:
    """Adresse eines neuen Gastes."""

    plz: str
    """Postleitzahl eines neuen Gastes."""

    ort: str
    """Ort eines neuen Gastes."""


@strawberry.input
class BuchungInput:
    """Buchung zu einem neuen Gast."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""

    zimmerkategorie: Zimmerkategorie
    """Zimmerkategorie."""

    verpflegung: Verpflegung
    """Verpflegung."""

    zahlungsart: Zahlungsart
    """Zahlungsart."""

    anreise: date
    """Anreisedatum."""

    abreise: date
    """Abreisedatum."""

    anzahl_gaeste: int
    """Anzahl der Gäste."""


@strawberry.input
class GastInput:
    """Daten für einen neuen Gast."""

    vorname: str
    """Vorname."""

    nachname: str
    """Nachname."""

    email: str
    """Emailadresse."""

    treuestufe: int
    """Treuestufe."""

    has_newsletter: bool
    """Angabe, ob der Newsletter abonniert ist."""

    geburtsdatum: date
    """Geburtsdatum."""

    homepage: str | None
    """Optionale Homepage."""

    adresse: AdresseInput
    """Adresse."""

    buchungen: list[BuchungInput]
    """Buchungen."""

    username: str
    """Benutzername."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Gast angelegt wurde."""

    id: int
    """ID des neu angelegten Gastes"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # ruff: ignore[mixed-case-variable-in-class-scope]  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
