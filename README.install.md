# Installation von Hotelgast

> Preview in VS Code durch `<Strg><Shift>v`

## Voraussetzung

Die Installation setzt voraus, dass _Python_ ab Version 3.15 installiert ist (siehe
`requires-python` in `pyproject.toml`), z.B. für Windows von
`https://www.python.org/downloads/windows`; der _install manager_ wird **NICHT**
benötigt. Für macOS gibt es z.B. `https://www.python.org/downloads/macos`.
Ob Python erfolgreich installiert ist, kann man folgendermaßen überprüfen:

```shell
    python --version
```

Evtl. muss man bei Windows noch die beiden Pfade `C:\<INSTALLATIONSVERZEICHNIS>`
und `C:\<INSTALLATIONSVERZEICHNIS>\Scripts` in die Umgebungsvariable `PATH`
aufnehmen.

Außerdem werden _Docker_ (für PostgreSQL, Keycloak und Mailpit) sowie _Git_ benötigt.

### Rust und Cargo für Source-Code-Distributionen

Falls für ein Package kein fertiges Wheel für die verwendete Python-Version existiert,
muss es aus dem Quellcode gebaut werden. Dazu wird Rust benötigt: Man lädt sich von
`https://rustup.rs` die Datei `rustup-init.exe` herunter und führt sie aus. Danach
muss `%USERPROFILE%\.cargo\bin` in der Umgebungsvariablen `PATH` enthalten sein.

## Installation von uv als Projektmanager

```shell
    # Windows:
    powershell -ExecutionPolicy ByPass -c 'Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression'

    # macOS/Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh
```

Danach ergänzt man die Umgebungsvariable `PATH` bei Windows um den Eintrag
`$env:USERPROFILE\.local\bin` und bei macOS sowie Linux um `$HOME/.local/bin`.
In einer _neuen_ Shell kann man dann z.B. `uv --version` aufrufen.

## Projekt holen

```shell
    git clone https://github.com/kobe1022/hotel.git
    cd hotel
```

## Abhängigkeiten installieren und implizit .venv erstellen

```shell
    uv sync --all-groups
```

## Backend-Server

Vor dem Start des Appservers müssen die Backend-Server für PostgreSQL, Keycloak und
Mailing gestartet sein. Zur Konfiguration gibt es im jeweiligen Unterverzeichnis eine
`ReadMe.md` Datei:

- PostgreSQL: `extras\compose\postgres\ReadMe.md`
- Keycloak: `extras\compose\keycloak\ReadMe.md`
- Mailing: `extras\compose\mailpit\ReadMe.md`

Beim ersten Start muss in _Keycloak_ der Realm `python` mit dem Client `python-client`
angelegt werden (siehe `extras\compose\keycloak\ReadMe.md`). Das _Client Secret_ des
Clients muss mit dem Eintrag `client-secret` in
`src\gast\config\resources\app.toml` übereinstimmen, siehe den Abschnitt
_Client Secret_ in der `ReadMe.md` von Keycloak.

Die drei Backend-Server startet man gemeinsam mit einem einzigen Kommando. Die
Compose-Datei für _Keycloak_ bindet dabei _PostgreSQL_ ein:

```shell
    # Windows:
    cd extras\compose
    docker compose -f keycloak\compose.yml -f mailpit\compose.yml up -d

    # macOS/Linux:
    cd extras/compose
    docker compose -f keycloak/compose.yml -f mailpit/compose.yml up -d
```

Mit demselben Kommando, aber mit `down` statt `up -d`, werden sie wieder heruntergefahren.
Alternativ startet man sie einzeln im jeweiligen Unterverzeichnis mit `docker compose up`.

## Applikationsserver

Durch das Kommando `uv run gast` kann man den Server starten (siehe `project.scripts`
in `pyproject.toml`). Er läuft mit TLS auf `https://localhost:8000`.

## Tests mit pytest

Die Unit- und Integrationstests werden folgendermaßen aufgerufen, nachdem der Appserver
gestartet ist:

```shell
    uv run pytest
```

## Bruno

Mit _Bruno_ und der Collection in `extras\bruno\gast` kann nun die REST- und
GraphQL-Schnittstelle des Applikationsservers benutzt werden (siehe
`extras\bruno\ReadMe.md`).

## Docker Image

Das Standard-Image auf Basis von _Alpine_ wird folgendermaßen gebaut:

```shell
    docker buildx bake
```

Das _hardened_ Image auf Basis von _Debian 13_ benötigt einen Zugang zu `dhi.io`
(`docker login dhi.io`) und wird folgendermaßen gebaut:

```shell
    docker build -t gast:0.1.0-hardened .
```

## Docker Container

Um alles gemeinsam zu starten, also den Appserver als Docker Container zusammen mit
PostgreSQL, Keycloak und Mailpit, setzt man folgende Kommandos ab. Die Backend-Server
dürfen dann natürlich noch nicht einzeln gestartet sein:

```shell
    # Windows:
    cd extras\compose\gast

    # macOS/Linux:
    cd extras/compose/gast

    docker compose up
```

Beendet wird mit `Strg+C` und anschließend `docker compose down` im selben Verzeichnis.

## Dokumentation

Um die Dokumentation auf Basis von _mkdocs_ als Webserver zu starten, darf der eigene
Applikationsserver nicht gestartet sein, weil _mkdocs_ ebenfalls den bei Python üblichen
Port `8000` nutzt. Für die UML-Diagramme werden _Java_, _Graphviz_ und `plantuml.jar`
benötigt (siehe den Abschnitt _Dokumentation_ in `README.md`). Den Server für _mkdocs_
startet man dann folgendermaßen:

```shell
    uv run --group doc mkdocs serve
```
