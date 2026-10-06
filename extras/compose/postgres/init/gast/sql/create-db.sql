-- Aufruf:   psql --dbname=postgres --username=postgres --file=/init/gast/sql/create-db.sql

-- https://www.postgresql.org/docs/current/sql-createuser.html
-- https://www.postgresql.org/docs/current/sql-createrole.html
CREATE USER gast PASSWORD 'p';

-- https://www.postgresql.org/docs/current/sql-createdatabase.html
CREATE DATABASE gast;

-- https://www.postgresql.org/docs/current/role-attributes.html
-- https://www.postgresql.org/docs/current/ddl-priv.html
-- https://www.postgresql.org/docs/current/sql-grant.html
GRANT ALL ON DATABASE gast TO gast;

-- https://www.postgresql.org/docs/current/sql-createtablespace.html
CREATE TABLESPACE gastspace OWNER gast LOCATION '/tablespace/gast';
