# Hinweise zur Konfiguration von Mailpit

## Named Volume

Die Daten zu den eingegangenen Emails werden im _Named Volume_ `mailpit`
abgespeichert, was deshalb zuvor erzeugt werden muss.

```shell
    docker volume create mailpit
```

## Mailpit als Mailserver starten

In einer PowerShell oder Bash wird _Mailpit_ als Docker Container gestartet.
Dabei werden die Daten zu den eingegangenen Emails im _Named Volume_ `mailpit`
abgespeichert.

```shell
    cd extras/compose/mailpit
    docker compose up
```

Der SMTP-Server ist unter `localhost:1025` erreichbar. Das passt zu den
Einstellungen im Abschnitt `[mail]` von `src/gast/config/resources/app.toml`.

## Test-Mail abschicken

Wenn der Server für die Gäste läuft, wird beim Anlegen eines neuen Gastes
(`POST /rest`) automatisch eine Email an die Rezeption geschickt.

Alternativ kann man mit Python eine Test-Mail abschicken:

```shell
    python -c "import smtplib; from email.message import EmailMessage; m = EmailMessage(); m['From'] = 'sender@acme.com'; m['To'] = 'recipient@acme.com'; m['Subject'] = 'My Subject'; m.set_content('My message body'); smtplib.SMTP('localhost', 1025).send_message(m)"
```

## Web-Oberfläche von Mailpit

_Mailpit_ beinhaltet einen Webserver, so dass man in einem Webbrowser überprüfen
kann, ob die Email angekommen ist. Dazu ruft man in einem Webbrowser die URL
`http://localhost:8025` auf.

## Herunterfahren und Beenden

Der Mailserver bzw. _Mailpit_ wird im Verzeichnis `extras/compose/mailpit`
mit `docker compose down` heruntergefahren.
