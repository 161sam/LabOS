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

## 3.3 Projekt-Doku

Pfad: `docs/`

Aufgabe:

* Architektur-, Modul- und Setup-Dokumentation für Repo-Besucher (GitHub-Oberfläche, Kontributoren, Betreiber)
* Einstiegspunkte: `docs/README.md`, `docs/overview.md`, `docs/architecture.md`, `docs/getting-started.md`, `docs/development.md`, `docs/contributing.md`
* Modul-Tiefe unter `docs/modules/`

Regeln:

* Markdown-first
* neue Fachmodule bekommen eine eigene Datei unter `docs/modules/` — **nicht** in die Root-README einhängen
* Architektur- und Boundary-Änderungen → `docs/architecture.md` aktualisieren
* Setup-/Dev-Änderungen → `docs/getting-started.md` bzw. `docs/development.md` aktualisieren
* Doku strukturell konsistent halten, keine Parallelwelten erzeugen

## 3.4 Runtime-Wiki

Pfad: `docs/wiki`

Aufgabe:

* Projektwissen innerhalb LabOS (wird zur Laufzeit vom Wiki-Modul ausgeliefert)
* SOPs, How-tos, Tutorials, Betriebshinweise

Regeln:

* Markdown-first
* sauber strukturiert
* von UI/Features aus sinnvoll referenzierbar
* technische und fachliche Doku trennen, wenn nötig
* Inhalte mit dauerhafter Relevanz für Betreiber gehören hier hin; Repo-/Architektur-Doku gehört nach `docs/`

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

LabOS ist im Zielbild **nicht selbst das Brain**. Die Zielarchitektur ist:

```
Smolit-AI-Assistant  →  ABrain  →  LabOS MCP / Tool Adapter  →  LabOS API / DB
```

Rollenverteilung:

- **LabOS** = Domain-, Realitäts- und Tool-/State-System
  (ReactorOps, Telemetrie, Commands, Safety, Assets, Inventory, Vision, Scheduler, Operator-UI, lokale fachliche Guards)
- **ABrain** = Brain, Governance, Planning, Execution Control, Trace, Audit, agentische Orchestrierung
- **Smolit-AI-Assistant** = User-Interaktion, Sprache, UX, Chat

Entscheidungsregel:

- LabOS beschreibt und kontrolliert die Laborrealität.
- ABrain entscheidet, plant und regiert die Ausführung.
- Der Smolit-AI-Assistant spricht mit dem Menschen.

Die `/api/v1/abrain/*`-Routen in LabOS sind seit **Adapter Alignment V1 Phase 2** eine Thin-Adapter-Facade: Status und Query delegieren an `abrain_adapter`; die Legacy-Schicht hält lediglich die bestehende UI-Kompatibilität. Der Zielendpunkt für LabOS bleibt ein sauber andockbarer MCP-Server / Tool-Adapter.

### LabOS SOLL NICHT

- eigene Planungs- oder Reasoning-Logik als Hauptpfad bauen
- agentische Orchestrierung als zweites Brain aufbauen
- ABrain-Governance oder Approval-Flows duplizieren
- den lokalen ABrain-Stub als Zielarchitektur weiter ausbauen
- UI-/Chat-Ebene vor die Brain-Ebene stellen
- in Rules, Scheduler, Vision oder Reactor-Health implizite Entscheidungs-, Planungs- oder Orchestrierungslogik einführen
- aus einer Klassifikation (z. B. `health_status=warning`, `vision.health_label=contamination_suspected`) automatisch Tasks/Commands erzeugen
- Command-Blockierungen außerhalb des Safety-Guards einführen

### LabOS SOLL

- Domain-State und Kontext sauber modellieren (Reaktoren, Safety, Telemetrie, Vision, Tasks, Alerts, Inventory, Assets)
- Actions/Tools klar definieren, stabil halten und über einen Action-Katalog beschreiben
- die MCP-/Tool-Adapter-Schicht sauber vorbereiten (Context Builder, Action Catalog, Governance Boundary, Response/Trace Mapping)
- Safety- und Domain-Guards lokal behalten (Kalibrierung, Safety-Incidents, Command-Guard)
- ABrain sauber andocken statt ersetzen
- Reactor-Health und Vision als **Classification + Signal Emission** halten (Signale liefern, nicht entscheiden)
- lokale Automation (Rule Engine, Scheduler-Dispatch) **als Fallback markieren** (`execution_origin='labos_local'`) und nicht als Hauptentscheidungslogik weiter ausbauen
- `blocked_reason`-Strings im Command-Pfad mit `safety_guard:` prefixen, damit die Absicht im API-Response sichtbar ist

Boundary Hardening V1 ist umgesetzt (Modul-Docstrings in `rules.py`, `scheduler.py`, `reactor_health.py`, `vision.py`, `safety.py`, `reactor_control.py`, `mqtt_bridge.py`, `abrain.py`; neuer `signals.py`-Helper; Invariant-Tests in `test_boundary_invariants.py`).

Phase 1 der Adapter-Andockung ist umgesetzt: `app/services/abrain_context.py`, `app/services/abrain_actions.py`, `app/services/abrain_client.py`, `app/services/abrain_adapter.py`, Router-Endpunkte `/api/v1/abrain/actions`, `/api/v1/abrain/adapter/context`, `/api/v1/abrain/adapter/query`, Frontend-Console `ABrainAdapterConsole`.

Phase 2 ist umgesetzt: `services/abrain.py` enthält **keine eigene Reasoning- oder Fallback-Logik mehr**. `get_status()` und `query()` delegieren an `abrain_adapter`; der einzige HTTP-Pfad nach ABrain ist `abrain_client.py`. Kein neues Reasoning darf zurück in `services/abrain.py` geschrieben werden — Änderungen gehören in den Adapter oder ins externe ABrain. Weitere Ausbaustufen (vollwertiger MCP-Server, Audit-Log, ABrain V2 Reasoning) folgen — nicht in LabOS-Kerngeschäft ziehen.

Phase 3 (Execution + Governance Flow) ist umgesetzt: `services/abrain_execution.py` ist der **einzige** Pfad, auf dem ABrain-Aktionen auf LabOS-Seiteneffekte gemappt werden. Dispatch erfolgt ausschließlich über das statische `ACTION_MAP` (`labos.create_task`, `labos.create_alert`, `labos.create_reactor_command`, `labos.retry_reactor_command`, `labos.ack_safety_incident`); keine Reflection, kein Dynamic Registry, keine Feldmatch-Heuristiken. Die Pipeline ist Catalog-Lookup → Role-Check (`descriptor.allowed_roles`) → Approval-Gate (`requires_approval` ohne `approve=True` → `pending_approval`, **keine Ausführung**) → Service-Dispatch → Result-Klassifikation (`blocked` erkennt `safety_guard:`-Ergebnisse aus `reactor_control` / `safety.check_command_guards`) → `ABrainExecutionLog`. Jeder Versuch — `executed`, `pending_approval`, `blocked`, `rejected`, `failed` — wird mit `action`, `params`, `trace_id`, `source`, `executed_by` persistiert (Migration `20260419_0018`). Endpoint: `POST /api/v1/abrain/execute`. Regel für Folgeänderungen: neue Actions werden nur nach Review in `ACTION_MAP` (nicht dynamisch) aufgenommen, und Governance-/Reasoning-Logik bleibt im Adapter bzw. externen ABrain — `abrain_execution.py` ist reine Enforcement- und Audit-Schicht.

Approval System V1 (HITL + Queue + UI + Audit) ist umgesetzt: `services/approvals.py` + `ApprovalRequest`-Modell (Migration `20260419_0019`) bilden den Queue-/State-Layer für approval-pflichtige Actions. Der `pending_approval`-Branch in `abrain_execution.execute_action` legt beim ersten Durchlauf eine `ApprovalRequest` an (Status `pending`, mit `action_name`, `action_params`, `trace_id`, `risk_level`, `requested_by_source`, `requested_via`, `reason`). Entscheidungen laufen über `POST /api/v1/approvals/{id}/approve|reject` — viewer sind 403, operator darf low/medium, nur admin darf high/critical. `approve_request` ruft `execute_action` mit `approve=True` erneut auf; **Safety- und Rollen-Guards werden dort erneut geprüft**, ein blockiertes Ergebnis landet als `ApprovalRequest.status='failed'` mit `blocked_reason` im Audit. Approval ist damit explizit **Release, kein Safety-Bypass**. Regel für Folgeänderungen: ABrain-Governance (Planung, Multi-Step-Workflows, Delegation, Ablaufsteuerung) bleibt im externen ABrain — LabOS liefert nur das lokale HITL-Gate und das Audit. Keine neuen Approval-Flows ohne Eintrag im `ACTION_MAP` und ohne `requires_approval`-Deskriptor.

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

## 7.1 README vs. docs/ — klare Trennung

Die Root-`README.md` ist **Einstiegspunkt**, kein Langform-Wiki.

Root-README:

* kurzer, klarer GitHub-Einstieg
* Produktpositionierung, Features-Überblick, Status
* verweist nach `docs/` für Tiefe
* **keine** langen API-Endpunktlisten
* **keine** vollständigen Modul-/Feldbeschreibungen
* **keine** V1-Unterkapitel mit Detail-Schemas
* darf nicht unkontrolliert wachsen

`docs/`-Baum:

* `docs/README.md` — Navigations-Hub
* `docs/overview.md` — Produktbild, V1-Scope, Leitprinzipien
* `docs/architecture.md` — Zielarchitektur, Boundary, Komponenten
* `docs/getting-started.md` — lokales Setup
* `docs/development.md` — Tests, Migrationen, Frontend-Build
* `docs/contributing.md` — Workflow, Commit-Stil
* `docs/modules/<modul>.md` — Fachmodul-Tiefe (Endpoints, Felder, Enums, UI-Flows, Grenzen)

Jede neue Modul-/Architektur-/Workflow-Dokumentation gehört grundsätzlich nach `docs/`. Die README soll eher Überblick, Navigation und Positionierung liefern.

## 7.2 Diese Dateien aktuell halten

Bei relevanten Änderungen prüfen und ggf. aktualisieren:

* `README.md` (nur, wenn Einstieg, Feature-Überblick oder Positionierung betroffen ist)
* `ROADMAP.md`
* `AGENTS.md`
* `docs/architecture.md` (bei Architektur-/Boundary-Änderungen)
* `docs/getting-started.md` oder `docs/development.md` (bei Setup-/Dev-Änderungen)
* passende Datei unter `docs/modules/` (bei Modul-Änderungen)
* Runtime-Wiki unter `docs/wiki/` (bei SOP-/How-to-Änderungen)
* API-bezogene Dokumentation

## 7.3 Keine Doku-Lücken bei Strukturänderungen

Wenn Ordner, Services, APIs oder Workflows geändert werden, muss die Doku im selben Arbeitsschritt mitgezogen werden.

## 7.4 Neue Module → neue Modul-Doku

Bei größeren Feature-Erweiterungen grundsätzlich:

1. passendes Dokument unter `docs/modules/` anlegen oder ergänzen
2. Link-Eintrag in `docs/README.md` setzen
3. ggf. kurzer Hinweis im Feature-Abschnitt der Root-README
4. ROADMAP-Eintrag aktualisieren

Nicht: ganze Modulbeschreibungen in die Root-README schreiben.

## 7.5 Runtime-Wiki ist Teil des Produkts

`docs/wiki/` (SOPs, How-tos, Tutorials) nicht als Nebensache behandeln. Es ist eigenständig von der Repo-Doku zu unterscheiden: Repo-/Architektur-Doku gehört nach `docs/`, Betriebswissen nach `docs/wiki/`.

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
