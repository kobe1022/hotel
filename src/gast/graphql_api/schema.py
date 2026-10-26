"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""

from dataclasses import asdict
from typing import Final
lazy from collections.abc import Sequence

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.extensions import PydanticErrorExtension
from strawberry.fastapi import GraphQLRouter
lazy from strawberry.types import Info

from gast.config.graphql import graphql_ide
from gast.graphql_api.graphql_types import (
    CreatePayload,
    GastInput,
    LoginResult,
    Suchparameter,
)
from gast.repository import GastRepository, GastSuchparameter, Pageable
from gast.router.gast_model import GastModel
from gast.security import Role, TokenService, UserService
from gast.service import (
    GastDTO,
    GastService,
    GastWriteService,
    NotFoundError,
)

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type Gast {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     gast(gast_id: ID!): Gast!
#     gaeste(suchparameter: Suchparameter): list[Gast!]!
# }


_repo: Final = GastRepository()
_service: GastService = GastService(repo=_repo)
_user_service: UserService = UserService()
_write_service: GastWriteService = GastWriteService(
    repo=_repo,
    user_service=_user_service,
)
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Gastdaten zu lesen."""

    @strawberry.field
    def gast(self, gast_id: strawberry.ID, info: Info) -> GastDTO | None:
        """Daten zu einem Gast lesen.

        :param gast_id: ID des gesuchten Gastes
        :return: Gesuchter Gast
        :rtype: Gast
        :raises NotFoundError: Falls kein Gast gefunden wurde, wird zu GraphQLError
        """
        logger.debug("gast_id={}", gast_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            gast_dto: Final = _service.find_by_id(
                gast_id=int(gast_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", gast_dto)
        return gast_dto

    @strawberry.field
    def gaeste(
        self,
        suchparameter: Suchparameter | None,
        info: Info,
    ) -> Sequence[GastDTO]:
        """Gäste anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Gäste
        :rtype: list[Gast]
        :raises NotFoundError: Falls kein Gast gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_filtered = (
            None
            if suchparameter is None
            else GastSuchparameter(
                email=suchparameter.email,
                nachname=suchparameter.nachname,
            )
        )
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            gaeste_dto: Final = _service.find(
                suchparameter=suchparameter_filtered,
                pageable=pageable,
            )
        except NotFoundError:
            return []
        logger.debug("{}", gaeste_dto)
        return gaeste_dto.content


@strawberry.type
class Mutation:
    """Mutations, um Gastdaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, gast_input: GastInput) -> CreatePayload:
        """Einen neuen Gast anlegen.

        :param gast_input: Daten des neuen Gastes
        :return: ID des neuen Gastes
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("gast_input={}", gast_input)

        # Dictonary mit Pydantic validieren
        gast_model: Final = GastModel.model_validate(asdict(gast_input))

        gast_dto: Final = _write_service.create(gast=gast_model.to_gast())
        payload: Final = CreatePayload(id=gast_dto.id)

        logger.debug("{}", payload)
        return payload

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # https://strawberry.rocks/docs/extensions/pydantic_error_extension
    extensions=[
        PydanticErrorExtension,
    ],
)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
