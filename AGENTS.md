# AGENTS.md

## Zweck dieser Datei

Diese Datei definiert die Arbeitsregeln für Agenten, Codex-Workflows und automatisierte Entwicklung im LabOS-Repository.

LabOS ist keine generische Demo-App, sondern eine spezialisierte Laborplattform für Raspberry Pi 4/5 mit Fokus auf:
- Chargenverwaltung
- Reaktorverwaltung
- Sensorik
- Wiki/Dokumentation
- Aufgaben/Planung
- Automatisierung
- ABrain-Anbindung
- Vision-/Bilddaten
- lokale/offline-fähige Nutzung

Alle Änderungen müssen diesem Produktziel dienen.

---

# 1. Arbeitsprinzipien

## 1.1 Produktprinzip
Arbeite so, dass LabOS als reales operatives System wächst, nicht als lose Tech-Demo.

## 1.2 Klein und sauber
Bevorzuge kleine, klare, testbare Änderungen statt großer unübersichtlicher Umbauten.

## 1.3 Raspberry-Pi-Tauglichkeit
Jede technische Entscheidung muss Pi-4/Pi-5-Tauglichkeit berücksichtigen:
- RAM
- CPU-Last
- Storage
- Build-Zeit
- Container-Größe
- Browser-Performance

## 1.4 Local first
Cloud-Annahmen vermeiden. Lokaler Betrieb muss immer möglich bleiben.

## 1.5 Dokumentation gehört zum Produkt
Wenn sich Verhalten, Struktur, API oder Setup ändern, muss die relevante Dokumentation mit aktualisiert werden.

## 1.6 Keine unnötige Komplexität
Nur so viele Abstraktionen, Services und Libraries einführen, wie real nötig sind.

## 1.7 Operativer Nutzen vor AI-Hype
AI, LLM und Vision sind Module. Sie ersetzen nicht:
- sauberes Datenmodell
- gutes UI
- klare Workflows
- nachvollziehbare Automatisierung

---

# 2. Aktuelle Projektstruktur

```text
LabOS/
├── apps/
│   └── frontend/
├── services/
│   └── api/
├── docs/
│   └── wiki/
├── configs/
├── scripts/
├── storage/
├── infra/
├── docker-compose.yml
├── README.md
├── ROADMAP.md
└── AGENTS.md
````

---

# 3. Verantwortungsbereiche im Repo

## 3.1 Frontend

Pfad: `apps/frontend`

Aufgabe:

* UI
* Routing
* Formulare
* Tabellen
* Dashboards
* Charts
* Wiki-Ansichten
* Bedienlogik

Regeln:

* einfache, klare Komponenten
* keine unnötig schweren UI-Frameworks
* mobile/touch-fähig mitdenken
* Datenzugriffe sauber kapseln
* Fehler- und Loading-Zustände nie auslassen

## 3.2 API

Pfad: `services/api`

Aufgabe:

* REST-API
* Datenmodell
* Validierung
* CRUD
* Integrationspunkte
* Business-Logik
* Persistenz
* Tests

Regeln:

* Router schlank halten
* Logik in Services auslagern, sobald sie wächst
* keine Geschäftslogik im Seed verstecken
* Schemas und Modelle konsistent halten
* Health/Readiness stabil halten

## 3.3 Wiki/Docs

Pfad: `docs/wiki`

Aufgabe:

* Projektwissen
* SOPs
* How-tos
* Tutorials
* Betriebshinweise
* Dev Docs

Regeln:

* Markdown-first
* sauber strukturiert
* von UI/Features aus sinnvoll referenzierbar
* technische und fachliche Doku trennen, wenn nötig

## 3.4 Configs

Pfad: `configs`

Aufgabe:

* Beispielkonfigurationen
* Standardprofile
* Dokumentation für Konfiguration

Regeln:

* keine Secrets einchecken
* immer `.example`/Beispielkonfiguration pflegen

## 3.5 Storage

Pfad: `storage`

Aufgabe:

* lokale Laufzeitdaten
* Fotos
* Wiki-Dateien
* Uploads

Regeln:

* keine unnötigen Binärdateien committen
* persistente Daten von Code trennen
* Volume-Nutzung sauber dokumentieren

---

# 4. Arbeitsmodus für Agenten

## 4.1 Immer zuerst verstehen

Vor Änderungen:

1. betroffene Dateien identifizieren
2. Datenfluss verstehen
3. bestehende Muster erkennen
4. nur dann erweitern oder vereinheitlichen

## 4.2 Bestehende Struktur respektieren

Nicht ohne Grund:

* Ordner umwerfen
* Namen umbenennen
* APIs brechen
* Dateistrukturen neu erfinden

## 4.3 Änderungen entlang fachlicher Pakete

Bevorzugte Einheiten:

* ein Modul
* ein CRUD-Flow
* ein klarer API-Bereich
* ein sauber abgegrenztes UI-Feature

## 4.4 Jede Änderung muss begründbar sein

Frage immer:

* Dient das dem Laborbetrieb?
* Dient das der Skalierbarkeit?
* Dient das der Wartbarkeit?
* Ist das auf Pi sinnvoll?

---

# 5. Coding-Regeln

## 5.1 Allgemein

* lesbarer Code vor cleverem Code
* kleine Funktionen
* sprechende Namen
* keine toten Pfade liegen lassen
* keine parallelen Implementationen erzeugen

## 5.2 Python / FastAPI

* Typen nutzen
* Pydantic/Schema sauber halten
* SQLModel/ORM-Nutzung konsistent halten
* Router klein halten
* Business-Logik nicht wild in `main.py` verteilen
* Konfiguration zentral halten

## 5.3 TypeScript / Next.js

* möglichst einfache Komponenten
* Logik nicht unnötig in Seiten aufblasen
* wiederverwendbare UI-Bausteine extrahieren
* keine wilden Inline-Datenzugriffe überall
* Lade- und Fehlerzustände sichtbar machen

## 5.4 Datenbank

* Schemaänderungen über Migrationen
* keine stillen Breaking Changes
* Statusfelder zentral definieren
* Relationen sauber und nachvollziehbar halten

---

# 6. Architekturregeln

## 6.1 Erst modularer Monolith, dann mehr

LabOS soll zunächst als modularer Monolith wachsen.
Nicht vorschnell:

* zusätzliche Services
* Event-Broker-Komplexität
* verteilte Orchestrierung
* künstliche Entkopplung

## 6.2 KI/ABrain als angebundene Schicht

ABrain ist Integrationspartner, nicht das Primärsystem für Datenspeicherung oder UI-Steuerung.

## 6.3 Vision separat andockbar

Vision-Funktionen so bauen, dass sie:

* lokal deaktivierbar sind
* optional bleiben
* keine Kernabläufe blockieren

## 6.4 Automatisierung nachvollziehbar

Jede Automationsaktion muss:

* sichtbar
* protokolliert
* im Zweifel deaktivierbar
  sein.

---

# 7. Doku-Regeln

## 7.1 Diese Dateien aktuell halten

Bei relevanten Änderungen prüfen und ggf. aktualisieren:

* `README.md`
* `ROADMAP.md`
* `AGENTS.md`
* Setup-Dokumente
* Wiki-Seiten
* API-bezogene Dokumentation

## 7.2 Keine Doku-Lücken bei Strukturänderungen

Wenn Ordner, Services, APIs oder Workflows geändert werden, muss die Doku im selben Arbeitsschritt mitgezogen werden.

## 7.3 Wiki ist Teil des Produkts

Wiki-Inhalte nicht als Nebensache behandeln.

---

# 8. Test- und Qualitätsregeln

## 8.1 Mindestanforderung pro Änderung

Jede nicht-triviale Änderung soll mindestens enthalten:

* funktionierenden Code
* passende Tests oder nachvollziehbare Begründung, warum noch keine Tests möglich sind
* aktualisierte Doku
* keine kaputten Builds

## 8.2 Backend

Mindestens testen, wenn betroffen:

* Health
* Kernrouten
* Validierung
* zentrale Services

## 8.3 Frontend

Mindestens prüfen:

* Rendering
* Datenabruf
* Fehlerzustände
* Basissichtbarkeit im Browser

## 8.4 Manuelle Prüfungen

Besonders wichtig bei:

* Formularen
* Tabellen
* Navigationsflüssen
* Touch-Bedienung
* Raspberry-Pi-Leistung

---

# 9. Git- und Commit-Regeln

## 9.1 Kleine Commits

Commits klein, thematisch sauber und nachvollziehbar halten.

## 9.2 Commit-Logik

Beispiele:

* `add charge create and edit flow`
* `introduce alembic migrations for core models`
* `add sensor ingest endpoint and dashboard widgets`
* `document local pi deployment`

## 9.3 Keine Misch-Commits

Nicht in einem Commit gleichzeitig:

* Refactor
* neues Feature
* Doku-Umbau
* Style-Fix
  wenn es vermeidbar ist.

## 9.4 Hauptbranch schützen

`main` soll möglichst stabil bleiben.

---

# 10. Bevorzugte nächste Arbeitspakete

Reihenfolge für die nächsten sinnvollen Umsetzungen:

1. Charge CRUD vollständig
2. Reaktor CRUD vollständig
3. Alembic-Migrationen
4. Sensoren + Sensorwerte
5. Tasks + Alerts
6. Wiki-UI ausbauen
7. Foto-Upload
8. ABrain mit echten LabOS-Daten koppeln
9. Automationsregeln
10. Auth + Rollen

Agenten sollen bevorzugt an diesen Paketen arbeiten und keine seitlichen Spielwiesen eröffnen.

---

# 11. Was vermieden werden soll

Nicht ohne guten Grund:

* komplettes Re-Scaffolding
* Framework-Wechsel
* schwere UI-Libraries nur für Optik
* vorschnelle Microservice-Aufspaltung
* undokumentierte API-Änderungen
* nicht nachvollziehbare Automatisierungslogik
* Cloud-Zwang
* KI-Funktionen ohne reale Datengrundlage
* Hardware-Annahmen ohne Pi-Realitätstest

---

# 12. Definition of Done für Agenten

Ein Task ist erst fertig, wenn:

1. die Anforderung fachlich umgesetzt ist
2. der Code lesbar und konsistent ist
3. relevante Tests ergänzt oder geprüft wurden
4. Doku aktualisiert wurde
5. Docker-/Dev-Setup nicht kaputt ist
6. keine offensichtlichen toten Enden zurückbleiben
7. Raspberry-Pi-Tauglichkeit mitbedacht wurde

---

# 13. Wenn größere Änderungen anstehen

Bei größeren Architekturänderungen zuerst:

1. Ziel klar benennen
2. betroffene Pfade benennen
3. Migrations-/Umbaupfad definieren
4. Risiken benennen
5. erst dann umsetzen

Größere Umbauten niemals blind im Repo verteilen.

---

# 14. Bevorzugte Arbeitsausgabe für Codex/Agenten

Wenn ein Agent an einem Arbeitspaket arbeitet, sollte die Abschlussausgabe möglichst enthalten:

## Kurzformat

* bearbeitetes Ziel
* warum dieser Schritt
* geänderte Dateien
* Ergebnis
* offene Punkte
* empfohlener nächster Schritt

## Bei Codearbeit zusätzlich

* exakte Shell-Befehle
* Commit-Vorschlag
* optional kurzer Testhinweis

---

# 15. Produktfokus für alle Folgearbeiten

LabOS ist im Kern:

* Labor-Betriebssystem
* digitale Betriebsdokumentation
* Monitoring- und Kontrollplattform
* Wissens- und Prozesssystem
* Assistenz- und Automatisierungsschicht

Jede Arbeit im Repo soll dieses Ziel stärken.
