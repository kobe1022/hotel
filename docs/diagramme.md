# Architektur und Diagramme

Die PlantUML-Quellen liegen unter `docs/diagramme/src/` und werden beim
`mkdocs`-Build automatisch nach SVG gerendert.

## Use-Case-Diagramm

Überblick über die Anwendungsfälle der Hotelgast-Verwaltung.

![Use-Case-Diagramm](diagramme/out/UseCaseDiagramm.svg)

## Komponentendiagramm

Architektur des Gast-Service: Router, Service- und Repository-Schicht.

![Komponentendiagramm](diagramme/out/Komponentendiagramm.svg)

## Schichtenarchitektur

Die Schichten des Gast-Service mit ihren wichtigsten Funktionen: Router, GraphQL,
Geschäftslogik, Datenbankzugriff und Entities.

![Schichtenarchitektur](diagramme/out/Schichtenarchitektur.svg)

## Klassendiagramm

Entity-Modell "Gast" mit den zugehörigen Entitäten.

![Klassendiagramm](diagramme/out/Klassendiagramm.svg)

## ER-Diagramm

Datenbankschema der `gast`-Datenbank (PostgreSQL).

![ER-Diagramm](diagramme/out/ErDiagramm.svg)

## Sequenzdiagramm: Neuen Gast anlegen

Ablauf von `POST /rest` vom Request bis zur Antwort.

![Sequenzdiagramm](diagramme/out/SequenzdiagrammGastAnlegen.svg)
