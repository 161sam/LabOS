# Contributing

LabOS ist ein Projekt mit klarem Produktfokus (Labor-Betriebssystem, Pi-tauglich, local first). Beiträge sollten diesem Fokus dienen.

## Workflow

1. Issue oder Konversation anlegen, um Scope und Zielbild zu klären.
2. Arbeitspaket klein halten (ein Modul, ein CRUD-Flow, ein UI-Feature).
3. Code + Tests + Doku gehören zusammen.
4. Pull Request mit aussagekräftigem Titel und kurzer Begründung.

Die Details und Invarianten stehen in [AGENTS.md](../AGENTS.md) — besonders:

- Abschnitt 1 (Arbeitsprinzipien)
- Abschnitt 4 (Arbeitsmodus)
- Abschnitt 6 (Architekturregeln, inkl. LabOS vs. ABrain vs. Smolit)
- Abschnitt 7 (Doku-Regeln)

## Dokumentation

- Die Root-[README](../README.md) ist Einstiegspunkt — sie bleibt bewusst knapp.
- Technische Tiefe gehört nach [`docs/`](./), nicht in die Root-README.
- Neue Fachmodule bekommen eine eigene Datei unter [`docs/modules/`](modules/).
- Architektur- oder Boundary-Änderungen → [architecture.md](architecture.md).

## Commit-Stil

Kurze, thematische Commits im Stil:

- `add charge create and edit flow`
- `introduce alembic migrations for core models`
- `add sensor ingest endpoint and dashboard widgets`
- `document local pi deployment`

Keine Misch-Commits (nicht Refactor + Feature + Doku-Umbau in einem Commit), wenn vermeidbar. `main` soll möglichst stabil bleiben.

## Qualitätskriterien (Definition of Done)

Ein Task ist fertig, wenn:

1. die Anforderung fachlich umgesetzt ist
2. Code lesbar und konsistent ist
3. relevante Tests ergänzt oder geprüft wurden
4. Doku aktualisiert wurde
5. Docker-/Dev-Setup funktioniert
6. keine offensichtlichen toten Enden zurückbleiben
7. Raspberry-Pi-Tauglichkeit mitbedacht wurde

## Was vermieden werden soll

- komplettes Re-Scaffolding, Framework-Wechsel
- schwere UI-Libraries nur für Optik
- vorschnelle Microservice-Aufspaltung
- undokumentierte API-Änderungen
- Cloud-Zwang, Hardware-Annahmen ohne Pi-Realitätstest
- LabOS zum zweiten Brain ausbauen — Planung/Governance gehört in ABrain

## Projekt-Status

LabOS befindet sich in aktiver Entwicklung (Pre-1.0). Öffentliche APIs können sich ändern; Breaking Changes werden über Migrationen und Release Notes kommuniziert.
