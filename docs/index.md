# Hotelgast

REST- und GraphQL-Service für die Verwaltung von Hotelgästen mit FastAPI,
SQLAlchemy, PostgreSQL, Keycloak und uv. Entstanden als Gruppenprojekt an der
Hochschule Karlsruhe.

## Autoren

- Benjamin Köken
- Aaron Stief

## Einrichtung

Voraussetzungen sind _uv_, Python `>=3.15` (siehe `requires-python` in
`pyproject.toml`) und _Docker_.

```shell
uv self update
uv sync --all-groups
```

Details zu Konfiguration, Compose-Stack (Keycloak, PostgreSQL, Mailpit) und
Tests siehe `README.md` im Repository-Root.

## Weiterführend

- [Architektur und Diagramme](diagramme.md)
