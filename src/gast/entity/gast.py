"""Entity-Klasse für Gastdaten."""

from typing import Self, override
lazy from datetime import date, datetime

from sqlalchemy import Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gast.entity.base import Base
lazy from gast.entity.adresse import Adresse
lazy from gast.entity.buchung import Buchung

# https://docs.python.org/3/library/dataclasses.html
# vgl.: record in Java, data class in Kotlin
# eq=False: __eq__ wird *NICHT* generiert, alternativ: eigene Methode __eq__
# repr=False: __repr__ wird *NICHT* generiert, alternativ: eigene Methode __repr__
# frozen=True: immutable
# slots=True: statt Speicherung in __dict__ -> schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
# kw_only=True: Initialisierungs-Fkt darf nur mit "Keyword Arguments" aufgerufen werden
# @dataclass(frozen=True, slots=True, kw_only=True)


# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models
# https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
# "frozen" und "slots" wird in SQLAlchemy noch nicht unterstuetzt
# https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types
# noinspection PyUnresolvedReferences
class Gast(Base):
    """Entity-Klasse für Gastdaten."""

    __tablename__ = "gast"

    # es gibt auch die "Build-in" Funktion id(objekt)
    # https://docs.python.org/3/library/functions.html#id
    # https://stackoverflow.com/questions/15667189/what-is-the-id-function-used-for#answer-15667328
    vorname: Mapped[str]
    """Der Vorname."""

    nachname: Mapped[str]
    """Der Nachname."""

    treuestufe: Mapped[int]
    """Die Treuestufe."""

    has_newsletter: Mapped[bool]
    """Angabe, ob der Newsletter abonniert ist."""
    # https://docs.python.org/3/library/datetime.html
    geburtsdatum: Mapped[date]
    """Das Geburtsdatum."""

    homepage: Mapped[str | None]
    """Die optionale URL der Homepage."""

    username: Mapped[str | None]
    """Der Benutzername für Login."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    email: Mapped[str] = mapped_column(unique=True)
    """Die eindeutige Emailadresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#relationship-configuration
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.innerjoin
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.cascade
    adresse: Mapped[Adresse | None] = relationship(
        # lambda seit SQLAlchemy 2.1
        # https://docs.sqlalchemy.org/en/21/changelog/migration_21.html#orm-relationship-allows-callable-for-back-populates
        # hier: keine Argumente, nur Rumpf des Lambda-Ausdrucks
        back_populates=lambda: Adresse.gast,
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    buchungen: Mapped[list[Buchung]] = relationship(
        back_populates=lambda: Buchung.gast,
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Buchungen."""

    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#column-defaults
    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    __mapper_args__ = {"version_id_col": version}  # ruff: ignore[mutable-class-default]

    def set(self, gast: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param gast: Gast-Objekt mit den aktuellen Daten
        """
        self.vorname = gast.vorname
        self.nachname = gast.nachname
        self.email = gast.email
        self.treuestufe = gast.treuestufe
        self.has_newsletter = gast.has_newsletter
        self.geburtsdatum = gast.geburtsdatum

    @override
    def __eq__(self, other: object) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    @override
    def __repr__(self) -> str:
        """Ausgabe eines Gastes als String, ohne Joins zu verursachen."""
        # Implizite String-Konkatenation
        return (
            f"Gast(id={self.id}, version={self.version}, "
            f"vorname={self.vorname}, nachname={self.nachname}, "
            f"email={self.email}, treuestufe={self.treuestufe}, "
            f"has_newsletter={self.has_newsletter}, "
            f"geburtsdatum={self.geburtsdatum}, homepage={self.homepage}, "
            f"username={self.username}, "
            f"erzeugt={self.erzeugt}, aktualisiert={self.aktualisiert})"
        )
