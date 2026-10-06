-- https://www.postgresql.org/docs/current/sql-dropindex.html
DROP INDEX IF EXISTS
    adresse_gast_id_idx,
    adresse_plz_idx,
    buchung_gast_id_idx,
    gast_nachname_idx;

-- https://www.postgresql.org/docs/current/sql-droptable.html
DROP TABLE IF EXISTS
    adresse,
    buchung,
    gast;

-- https://www.postgresql.org/docs/current/sql-droptype.html
DROP TYPE IF EXISTS
    zimmerkategorie,
    verpflegung,
    zahlungsart;
