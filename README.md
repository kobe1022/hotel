# Hotelgast

REST- und GraphQL-Service für die Verwaltung von Hotelgästen mit FastAPI, SQLAlchemy,
PostgreSQL, Keycloak und uv. Entstanden als Gruppenprojekt an der Hochschule Karlsruhe.

## Status

Vorhanden sind: Server mit TLS, Konfiguration, Entities, Repository,
PostgreSQL-Anbindung, Service-Schicht, REST- und GraphQL-Schnittstelle, Zugriffsschutz
mit Keycloak, Neuladen von Datenbank und Keycloak im Entwicklungsmodus, E-Mail-Versand
(Mailpit), Excel-Export, Tests, Lasttest (Locust), eine Bruno-Collection, Docker-Images
mit Docker Compose und die Dokumentation mit mkdocs (siehe
[Dokumentation](#dokumentation)).

## Autoren

- Benjamin Köken
- Aaron Stief

## Einrichtung

Voraussetzungen sind _uv_, Python `>=3.15` (siehe `requires-python` in
`pyproject.toml`) und _Docker_. Eine ausführliche Schritt-für-Schritt-Anleitung steht in
[README.install.md](README.install.md). In einer Shell (PowerShell bei Windows oder bash
bei macOS) im Projektverzeichnis:

```shell
    # uv aktualisiert sich ggf. selbst
    uv self update

    # Packages aus pyproject.toml installieren: dependencies und alle "dependency-groups"
    uv sync --all-groups
```

Bei VS Code wählt man durch die Funktionstaste _F1_ in der _Kommandopalette_ den
Eintrag _Python: Interpreter auswählen_ mit dem Unterpunkt `.\.venv\Scripts\python.exe`
aus. Dadurch wird der Python-Interpreter der virtuellen Umgebung verwendet, die mit
_uv_ angelegt wurde.

## Inhalt

- [Backend-Server](#backend-server)
- [Applikationsserver](#applikationsserver)
- [Docker Image und Container](#docker-image-und-container)
- [Anmeldung mit Keycloak](#anmeldung-mit-keycloak)
- [Testen](#testen)
- [Statische Codeanalyse](#statische-codeanalyse)
- [Analyse von Sicherheitslücken](#analyse-von-sicherheitslücken)
- [Dokumentation](#dokumentation)
- [Port bereits belegt?](#port-bereits-belegt)

## Backend-Server

Vor dem Start des Appservers müssen die Backend-Server für PostgreSQL und Keycloak
gestartet sein. Zur Konfiguration gibt es im jeweiligen Unterverzeichnis eine
`ReadMe.md` Datei:

- PostgreSQL: `extras\compose\postgres\ReadMe.md`
- Keycloak: `extras\compose\keycloak\ReadMe.md`

Für den E-Mail-Versand beim Anlegen eines Gastes gibt es _Mailpit_, siehe
`extras\compose\mailpit\ReadMe.md`.

Wenn die Backend-Server eingerichtet sind, kann man sie mit _Docker Compose_ starten.
Die Compose-Datei für _Keycloak_ bindet die für _PostgreSQL_ ein (`include`), sodass
beide Server gemeinsam gestartet werden:

```shell
    # Windows
    cd .\extras\compose\keycloak

    # macOS / Linux
    cd ./extras/compose/keycloak

    docker compose up
```

## Applikationsserver

Durch das Kommando `uv run gast` kann man den Server starten (siehe `project.scripts`
in `pyproject.toml`). Dabei wird _uvicorn_ als ASGI-Server verwendet.
Standardmäßig läuft der Server mit HTTPS auf Port `8000`. Die Einstellungen stehen in
`src\gast\config\resources\app.toml`.

Im Entwicklungsmodus (`[dev]` in `app.toml`) werden beim Start

- die Datenbank (`db-populate = true`) und
- Keycloak (`keycloak-populate = true`)

neu geladen. Für Keycloak werden dabei alle Benutzer außer `admin` gelöscht und die
Benutzer aus der CSV-Datei `extras\compose\postgres\init\gast\csv\gast.csv` mit der
Rolle `GAST` und dem Passwort `p` neu angelegt.

Als Administrator kann man Keycloak auch während des Betriebs durch einen
`QUERY`-Request auf `/dev/keycloak_populate` neu laden. Dazu ist ein Access Token
mit der Rolle `ADMIN` erforderlich.

## Docker Image und Container

Das Standard-Image auf Basis von _Alpine_ wird mit _docker buildx bake_ gebaut. Das
_hardened_ Image auf Basis von _Debian 13_ (`Dockerfile`) benötigt einen Zugang zu
`dhi.io` (`docker login dhi.io`):

```shell
    docker buildx bake
    docker build -t gast:0.1.0-hardened .
```

Der Applikationsserver kann einschließlich der Backend-Server als Container gestartet
werden. Dann dürfen die Backend-Server nicht schon einzeln laufen:

```shell
    # Windows
    cd .\extras\compose\gast

    # macOS / Linux
    cd ./extras/compose/gast

    docker compose up
```

Weitere Hinweise stehen in [README.install.md](README.install.md).

## Anmeldung mit Keycloak

Nachdem _Keycloak_ gemäß `extras\compose\keycloak\ReadMe.md` eingerichtet ist,
muss das _Client Secret_ des Clients `python-client` mit dem Eintrag `client-secret`
in `src\gast\config\resources\app.toml` übereinstimmen. Das Secret findet man in
Keycloak im Tab `Credentials` des Clients (siehe dort den Abschnitt _Client Secret_).

Es gibt die Rollen `ADMIN` und `GAST`. Einen Access Token erhält man durch einen
`QUERY`-Request auf `/auth/token` mit einem JSON-Datensatz im Request-Body:

```shell
    curl --insecure --http2 --request QUERY `
        --header "Content-Type: application/json" `
        --data '{"username": "admin", "password": "p"}' `
        https://localhost:8000/auth/token
```

Die Antwort enthält den Token, die Gültigkeitsdauer und die Rollen. Den Token übergibt
man bei weiteren Requests als _Bearer Token_ im Header `Authorization`.

## Testen

_pytest_ <https://docs.pytest.org> ist eine bessere Alternative zu _unittest_ aus der
Python-Distribution. Die Tests liegen unterhalb von `tests` und sind in
`tests\unit` und `tests\integration` aufgeteilt.

Vor Integrationstests müssen DB-Server, Keycloak-Server und Appserver gestartet sein.

```shell
    uv run pytest
    uv run pytest -m rest
    uv run pytest -k <Name_der_Testfunktion>
```

## Statische Codeanalyse

_ruff_ als Linter und _ty_ sowie _pyrefly_ als "Type Checker" werden als Tool für _uv_
installiert. Für YAML-Dateien gibt es zusätzlich _yamllint_:

```shell
    uv tool install ruff
    uv tool install ty
    uv tool install pyrefly
    uv tool install yamllint
```

Danach kann man diese Werkzeuge folgendermaßen aufrufen:

```shell
    ruff check [--preview] src tests
    ruff format [--preview] src tests

    ty check src tests/unit tests/integration
    pyrefly check --output-format full-text [--verbose]
    yamllint extras\compose mkdocs.yml
```

Die Konfiguration von _yamllint_ steht in `.yamllint.yml`. Die Konfiguration für
_markdownlint_, z.B. als Erweiterung in VS Code, steht in `.markdownlint.yml`.

## Analyse von Sicherheitslücken

Da der Linter _ruff_ auch die Regeln von _bandit_ implementiert, erfolgt durch den
Aufruf von ruff eine implizite Analyse im Hinblick auf Sicherheitslücken.

Mit _OWASP Dependency Check_ werden alle in `pyproject.toml` installierten Module mit
den _CVE_-Nummern der NIST-Datenbank abgeglichen. Von
<https://nvd.nist.gov/developers/request-an-api-key> fordert man einen "API Key" an und
trägt ihn in `.env` als Wert der Umgebungsvariablen `NVD_API_KEY` ein:

```shell
    uv run extras/dependency-check.py
```

Bekannte Sicherheitslücken in den verwendeten 3rd Party Packages prüft man mit:

```shell
    uv audit
```

## Dokumentation

Die Projektdokumentation wird mit _MkDocs_ (Theme _Material_) aus `docs/` erzeugt.
Die UML-Diagramme liegen als PlantUML-Quellen unter `docs/diagramme/src/` und werden
beim Build automatisch nach SVG gerendert (`docs/diagramme/out/`, nicht versioniert).

Für das lokale Rendering werden _Java_, _Graphviz_ (`dot`) sowie `plantuml.jar` benötigt.
Die Datei `plantuml.jar` kann an einem beliebigen Ort liegen, am besten außerhalb des
Projekts, z.B. in _PowerShell_:

```shell
    New-Item -ItemType Directory -Force C:\Tools\plantuml
    curl.exe -L -o C:\Tools\plantuml\plantuml.jar https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
    java -jar C:\Tools\plantuml\plantuml.jar -version
```

Der Aufruf wird über die Umgebungsvariable `PLANTUML_BIN` konfiguriert
(Default: `java -jar plantuml.jar`, siehe `mkdocs.yml`). _MkDocs_ liest die Datei `.env`
nicht, deshalb muss die Variable in der Shell gesetzt werden:

```shell
    # nur für die aktuelle PowerShell
    $env:PLANTUML_BIN = "java -jar C:/Tools/plantuml/plantuml.jar"

    # dauerhaft (danach eine neue Shell öffnen)
    setx PLANTUML_BIN "java -jar C:/Tools/plantuml/plantuml.jar"
```

Vorschau mit Live-Reload bzw. statischer Build nach `site/`:

```shell
    uv run --group doc mkdocs serve
    uv run --group doc mkdocs build --strict
```

Falls der Port `8000` belegt ist (z.B. durch den Server), startet man die Vorschau mit
`uv run --group doc mkdocs serve -a 127.0.0.1:8001`.

## Port bereits belegt?

Falls der Server nicht gestartet werden kann, weil z.B. der Port `8000` belegt ist,
kann man bei Windows in der PowerShell zunächst die ID vom Betriebssystem-Prozess
ermitteln, der den Port belegt, und danach diesen Prozess beenden:

```powershell
    netstat -ano | findstr ':8000'
    taskkill /F /PID <Prozess-ID>
```

Bei macOS:

```shell
    ps -af
    kill <Prozess-ID>
    # ggf.
    kill -9 <Prozess-ID>
```
