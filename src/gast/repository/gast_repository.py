# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Repository fuer persistente Gastdaten."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from gast.entity import Gast
from gast.repository.slice import Slice
lazy from gast.repository.gast_suchparameter import GastSuchparameter
lazy from gast.repository.pageable import Pageable

__all__ = ["GastRepository"]


class GastRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Gast."""

    def find_by_id(self, gast_id: int | None, session: Session) -> Gast | None:
        """Suche mit der Gast-ID.

        :param gast_id: ID des gesuchten Gastes
        :param session: Session für SQLAlchemy
        :return: Der gefundene Gast oder None
        :rtype: Gast | None
        """
        logger.debug("gast_id={}", gast_id)  # NOSONAR

        if gast_id is None:
            return None

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loading-with-loader-options
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.joinedload
        statement: Final = (
            select(Gast).options(joinedload(Gast.adresse)).where(Gast.id == gast_id)
        )
        gast: Final = session.scalar(statement)

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#get-by-primary-key
        # gast: Final[Gast | None] = session.get(Gast, gast_id)

        logger.debug("{}", gast)
        return gast

    def find(
        self,
        suchparameter: GastSuchparameter | None,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Gast]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Tupel, d.h. readonly Liste, der gefundenen Gäste oder leeres Tupel
        :rtype: Slice[Gast]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        if suchparameter is None or suchparameter.is_empty():
            return self._find_all(pageable=pageable, session=session)

        if suchparameter.email is not None:
            gast = self._find_by_email(email=suchparameter.email, session=session)
            logger.debug(log_str, gast)
            return (
                Slice(content=(gast,), total_elements=1)
                if gast is not None
                else Slice(content=(), total_elements=0)
            )

        if suchparameter.nachname is not None:
            gaeste = self._find_by_nachname(
                teil=suchparameter.nachname,
                pageable=pageable,
                session=session,
            )
            logger.debug(log_str, gaeste)
            return gaeste

        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Gast]:
        logger.debug("aufgerufen")
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Gast)
                .options(joinedload(Gast.adresse))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (select(Gast).options(joinedload(Gast.adresse)))
        )
        gaeste: Final = (session.scalars(statement)).all()
        anzahl: Final = self._count_all_rows(session)
        gast_slice: Final = Slice(content=tuple(gaeste), total_elements=anzahl)
        logger.debug("gast_slice={}", gast_slice)
        return gast_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Gast)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def _find_by_email(self, email: str, session: Session) -> Gast | None:
        """Einen Gast anhand der Emailadresse suchen.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: Gefundener Gast, falls es einen Gast gibt, sonst None
        :rtype: Gast | None
        """
        logger.debug("email={}", email)  # NOSONAR
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            select(Gast).options(joinedload(Gast.adresse)).where(Gast.email == email)
        )
        gast: Final = session.scalar(statement)
        logger.debug("{}", gast)
        return gast

    def _find_by_nachname(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Gast]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Gast)
                .options(joinedload(Gast.adresse))
                .filter(Gast.nachname.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Gast)
                .options(joinedload(Gast.adresse))
                .filter(Gast.nachname.ilike(f"%{teil}%"))
            )
        )
        gaeste: Final = session.scalars(statement).all()
        anzahl: Final = self._count_rows_nachname(teil, session)
        gast_slice: Final = Slice(content=tuple(gaeste), total_elements=anzahl)
        logger.debug("{}", gast_slice)
        return gast_slice

    def _count_rows_nachname(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Gast)
            .filter(Gast.nachname.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Gast.email == email)
        anzahl: Final = session.scalar(statement)
        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def exists_email_other_id(
        self,
        email: str,
        gast_id: int,
        session: Session,
    ) -> bool:
        """Abfrage, ob es die Emailadresse bei einer anderen Gast-ID bereits gibt.

        :param email: Emailadresse
        :param gast_id: eigene Gast-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(Gast.id).where(Gast.email == email)
        id_db: Final = session.scalar(statement)
        logger.debug("id_db={}", id_db)
        return id_db is not None and id_db != gast_id

    def create(self, gast: Gast, session: Session) -> Gast:
        """Speichere einen neuen Gast ab.

        :param gast: Die Daten des neuen Gastes ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Gast mit generierter ID
        :rtype: Gast
        """
        logger.debug(
            "gast={}, gast.adresse={}, gast.buchungen={}",
            gast,
            gast.adresse,
            gast.buchungen,
        )
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=gast)
        # flush(), damit die ID aus der Sequence vor COMMIT fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[gast])
        logger.debug("gast_id={}", gast.id)
        return gast

    def update(self, gast: Gast, session: Session) -> Gast | None:
        """Aktualisiere einen Gast.

        :param gast: Die neuen Gastdaten
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Gast oder None, falls kein Gast mit der ID
        existiert
        :rtype: Gast | None
        """
        logger.debug("{}", gast)

        if (gast_db := self.find_by_id(gast_id=gast.id, session=session)) is None:
            # Gastdaten wurden i.a. zuvor in der Session aktualisiert
            return None

        # session.add(gast_db) nicht notwendig, da bereits in der Session zugegriffen
        # CAVEAT: Die erhoehte Versionsnummer ist erst *nach* COMMIT sichtbar

        logger.debug("{}", gast_db)
        return gast_db

    def delete_by_id(self, gast_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Gast.

        :param gast_id: Die ID des zu löschenden Gastes
        :param session: Session für SQLAlchemy
        """
        logger.debug("gast_id={}", gast_id)

        # delete(Gast).where(Gast.gast_id == gast_id) OHNE cascade
        # "walrus operator" https://peps.python.org/pep-0572
        if (gast := self.find_by_id(gast_id=gast_id, session=session)) is None:
            return
        session.delete(gast)
        logger.debug("ok")

    def find_nachnamen(self, teil: str, session: Session) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring zu den gesuchten Nachnamen
        :param session: Session für SQLAlchemy
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: Sequence[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Gast.nachname).filter(Gast.nachname.ilike(f"%{teil}%")).distinct()
        )
        nachnamen: Final = (session.scalars(statement)).all()

        logger.debug("nachnamen={}", nachnamen)
        return nachnamen

    def exists_username(self, username: str | None, session: Session) -> bool:
        """Abfrage, ob es den Benutzernamen bereits gibt.

        :param username: Benutzername
        :param session: Session für SQLAlchemy
        :return: True, falls es den Benutzernamen bereits gibt
        :rtype: bool
        """
        logger.debug("username={}", username)
        if username is None:
            return False

        statement: Final = select(Gast.username).filter_by(username=username)
        username_db: Final = session.scalar(statement)
        logger.debug("username_db={}", username_db)
        return username_db is not None
