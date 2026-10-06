-- Aufruf:   psql --dbname=gast --username=gast --file=/init/gast/sql/create-schema.sql

-- https://www.postgresql.org/docs/devel/app-psql.html
-- https://www.postgresql.org/docs/current/ddl-schemas.html
-- https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-CREATE
-- "user-private schema" (Default-Schema: public)
CREATE SCHEMA IF NOT EXISTS AUTHORIZATION gast;

ALTER ROLE gast SET search_path = 'gast';
