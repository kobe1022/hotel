"""Modul für die GraphQL-Schnittstelle."""

from gast.graphql_api.graphql_types import (
    AdresseInput,
    BuchungInput,
    CreatePayload,
    GastInput,
    Suchparameter,
)
from gast.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "AdresseInput",
    "BuchungInput",
    "CreatePayload",
    "GastInput",
    "Mutation",
    "Query",
    "Suchparameter",
    "graphql_router",
]
