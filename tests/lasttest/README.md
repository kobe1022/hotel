# Hinweise zu locust

> Preview in VS Code durch `<Strg><Shift>v`

## locust

_locust_ ist - neben _k6_ - ein weit verbreitetes Werkzeug für Lasttests und wird
eingesetzt, um Anwendungen z.B. in einer Cloud unter Last zu testen. Die Skripte werden
in Python implementiert.

## Vorbereitung

Wenn der zu testende Appserver als Docker Container gestartet wird, dann sollte man
Einstellungen wie z.B. ausführliche Log-Ausgaben, die für die Entwicklung hilfreich sind,
entfernen:

- die Umgebungsvariable `LOGURU_LEVEL=INFO` setzen
- in `src\gast\config\resources\app.toml`
  - bei der Table `[db]` die Property `log-statements` auskommentieren
  - bei der Table `[graphql]` die Property `graphiql-enabled` auskommentieren

Nun startet man die Backend-Server und den zu testenden Appserver.

## Aufruf

Der Aufruf von _locust_ erfolgt durch folgendes Kommando:

```shell
  cd tests/lasttest
  uvx locust
```

## Konfiguration und Start

Mit dem Aufruf von _locust_ wurden ein Webserver gestartet und in einem Webbrowser kann
man die URL `http://localhost:8089` aufrufen. In der Administrationsoberfläche setzt man
z.B. folgende Einstellungen:

- Number of users: `50`
- Ramp Up (users started/second): `5`
- Host: `https://localhost:8000`

Jetzt kann man den Button _Start_ anklicken.

## Interpretation der Ergebnisse

Bei der Interpretation möge man bedenken:

- Die Server-Infrastruktur besteht aus einem _Notebook_ und ist keine Server-Hardware.
- Auf dem Notebook läuft nicht nur der Appserver, sondern auch der _DB-Server_,
  _Keycloak-Server_, _Mailserver_ und der _Webserver für locust_.
- Sowohl der Appserver als auch die Backend-Server lauften _virtualisiert_ in einem
  _Container_.
- Die Container sind über ein virtuelles Netzwerk verbunden.
- Es wird _HTTPS_ genutzt und nicht nur HTTP.
- Spätestens jetzt wird klar, warum _web.de_ in ihren Anfangsjahren fast alles
  mit Python realisiert hat.
