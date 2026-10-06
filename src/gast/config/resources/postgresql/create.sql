-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- TEXT statt varchar(n):
-- "There is no performance difference among these three types, apart from a few extra CPU cycles
-- to check the length when storing into a length-constrained column"
-- ggf. CHECK(char_length(nachname) <= 255)

-- https://www.postgresql.org/docs/current/manage-ag-tablespaces.html
SET default_tablespace = gastspace;

-- https://www.postgresql.org/docs/current/sql-createtable.html
-- https://www.postgresql.org/docs/current/datatype.html
-- https://www.postgresql.org/docs/current/sql-createtype.html
-- https://www.postgresql.org/docs/current/datatype-enum.html
CREATE TYPE zimmerkategorie AS ENUM ('EINZELZIMMER', 'DOPPELZIMMER', 'FAMILIENZIMMER', 'JUNIOR_SUITE', 'SUITE', 'PRESIDENTIAL_SUITE');
CREATE TYPE verpflegung AS ENUM ('UEBERNACHTUNG', 'FRUEHSTUECK', 'HALBPENSION', 'VOLLPENSION', 'ALL_INCLUSIVE');
CREATE TYPE zahlungsart AS ENUM ('KREDITKARTE', 'BAR', 'UEBERWEISUNG', 'PAYPAL');

CREATE TABLE IF NOT EXISTS gast (
    id            INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    version       INTEGER NOT NULL DEFAULT 0,
    vorname       TEXT NOT NULL,
    nachname      TEXT NOT NULL,
                  -- impliziter Index als B-Baum durch UNIQUE
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS
    email         TEXT NOT NULL UNIQUE,
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS
    treuestufe    INTEGER NOT NULL CHECK (treuestufe >= 0 AND treuestufe <= 9),
                  -- https://www.postgresql.org/docs/current/datatype-boolean.html
    has_newsletter BOOLEAN NOT NULL DEFAULT FALSE,
                  -- https://www.postgresql.org/docs/current/datatype-datetime.html
    geburtsdatum  DATE CHECK (geburtsdatum < current_date),
    homepage      TEXT,
    username      TEXT NOT NULL,
                  -- https://www.postgresql.org/docs/current/datatype-datetime.html
    erzeugt       TIMESTAMP NOT NULL,
    aktualisiert  TIMESTAMP NOT NULL
);

-- default: btree
CREATE INDEX IF NOT EXISTS gast_nachname_idx ON gast(nachname);

CREATE TABLE IF NOT EXISTS adresse (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    plz         TEXT NOT NULL CHECK (plz ~ '\d{5}'),
    ort         TEXT NOT NULL,
    gast_id     INTEGER NOT NULL REFERENCES gast ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS adresse_gast_id_idx ON adresse(gast_id);
CREATE INDEX IF NOT EXISTS adresse_plz_idx ON adresse(plz);

CREATE TABLE IF NOT EXISTS buchung (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
                    -- https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-NUMERIC-DECIMAL
                    -- https://www.postgresql.org/docs/current/datatype-money.html
                    -- 10 Stellen, davon 2 Nachkommastellen
    betrag          NUMERIC(10,2) NOT NULL,
    waehrung        TEXT NOT NULL CHECK (waehrung ~ '[A-Z]{3}'),
    zimmerkategorie zimmerkategorie NOT NULL,
    verpflegung     verpflegung NOT NULL,
    zahlungsart     zahlungsart NOT NULL,
    anreise         DATE NOT NULL,
    abreise         DATE NOT NULL CHECK (abreise > anreise),
    anzahl_gaeste   INTEGER NOT NULL CHECK (anzahl_gaeste >= 1 AND anzahl_gaeste <= 10),
    gast_id         INTEGER NOT NULL REFERENCES gast ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS buchung_gast_id_idx ON buchung(gast_id);
