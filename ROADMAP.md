Du arbeitest im Repository **LabOS**.

Kontext:
LabOS entwickelt sich von einer einzelnen Labor-App zu einem modularen Operating System für EcoSphereLab.

LabOS ist nicht nur für Bio-Prozesse gedacht, sondern für ein reales Multi-Domain-Lab mit:
- BioOps
- MakerOps
- ITOps
- R&D Ops
- KnowledgeOps
- Automation
- AI Assistenz

Bereits umgesetzt:
- Charges CRUD
- Reactors CRUD
- Alembic Migrationen
- Sensorik V1
- Tasks + Alerts V1
- Photo Upload + Vision Basis V1
- ABrain Integration V1 mit echtem lab_context
- Dashboard-Basis
- Wiki-Basis

Stack:
- Frontend: Next.js
- Backend: FastAPI
- PostgreSQL
- Docker Compose

Wichtige Dateien:
- README.md
- ROADMAP.md
- AGENTS.md

---

# Deine Aufgabe

Baue als nächsten sauberen Entwicklungsschritt:

# Regelengine / Automation V1

Ziel:
LabOS soll kontrollierte, nachvollziehbare Regeln ausführen können, die auf bestehenden LabOS-Daten basieren.

Nach diesem Schritt soll LabOS können:

- Regeln definieren
- Regeln aktiv/inaktiv schalten
- Regeln manuell testen
- Regeln gegen aktuelle Daten evaluieren
- aus Regeln Tasks und/oder Alerts erzeugen
- Regelereignisse protokollieren

Wichtig:
Dieser Schritt soll keine vollautonome Hardwaresteuerung einführen.
Es geht um eine sichere, nachvollziehbare V1-Regelschicht für operative Reaktionen im Laborbetrieb.

---

# Warum dieser Schritt jetzt sinnvoll ist

LabOS hat genug operative Kernobjekte und Datenquellen:

## Datenquellen
- Sensorwerte
- Sensorstatus
- Tasks
- Alerts
- Charges
- Reactors
- später anschlussfähig für Assets, ITOps und weitere Bereiche

## Zielobjekte
- neue Alerts erzeugen
- neue Tasks erzeugen

Die Regelengine ist der nächste logische Schritt, bevor LabOS auf weitere Domänen wie Geräte, Inventory oder ITOps ausgeweitet wird.

---

# Wichtige Anforderungen

1. Bestehende Architektur respektieren.
2. Raspberry-Pi-tauglich bleiben.
3. Keine überkomplexe Workflow-Engine bauen.
4. Regeln müssen nachvollziehbar und protokolliert sein.
5. Kein Cloud-Zwang.
6. Keine versteckte Magie.
7. Keine Hardware-/GPIO-Aktionen in diesem Schritt.
8. Dokumentation aktualisieren.
9. Scope strikt halten.
10. Die Umsetzung soll später sauber auf weitere Domänen erweiterbar sein.

---

# Zielbild nach diesem Schritt

Nach diesem Schritt soll LabOS bieten:

- Rule-Modell in der DB
- einfache regelbasierte Evaluation
- UI für Regeln
- Dry-Run/Test-Funktion
- Event-/Execution-Log
- echte V1-Aktionen:
  - Task erzeugen
  - Alert erzeugen

---

# Scope

## 1. Datenmodell

Ergänze mindestens:

### Rule
Mindestens Felder wie:
- id
- name
- description
- is_enabled
- trigger_type
- condition_type
- condition_config
- action_type
- action_config
- created_at
- updated_at
- last_evaluated_at optional

Beispiele:
- trigger_type: sensor_threshold, stale_sensor, overdue_tasks
- condition_type: threshold_gt, threshold_lt, age_gt_hours, count_gt
- action_type: create_alert, create_task

### RuleExecution / RuleEvent
Mindestens:
- id
- rule_id
- status
- dry_run
- evaluation_summary
- action_result
- created_at

Status z. B.:
- matched
- not_matched
- executed
- failed

Wichtig:
- Protokollierung muss nachvollziehbar sein
- JSON/Text-basierte Zusammenfassungen sind okay
- nicht übermodellieren

---

## 2. Alembic Migration

Neue saubere Migration erstellen.

---

## 3. Backend Regel-Engine V1

Baue eine kleine, saubere Service-Schicht für:
- Regeln laden
- Regel validieren
- Regel evaluieren
- Action auslösen
- Execution loggen

Wichtig:
- keine große generische Engine
- lieber wenige klar unterstützte Regeltypen
- Code gut erweiterbar halten

---

## 4. Unterstützte V1-Regeln

Bitte bewusst klein halten.

Mindestens diese V1-Regeltypen:

### A. Sensor Threshold
Beispiel:
- Wenn Sensor X > Schwellwert -> Alert erzeugen
- Wenn Sensor X < Schwellwert -> Task erzeugen

### B. Stale Sensor
Beispiel:
- Wenn Sensor seit N Stunden keine Werte hat -> Alert erzeugen

### C. Overdue Tasks
Beispiel:
- Wenn offene Tasks überfällig sind -> Alert erzeugen

Optional klein, wenn sauber:
### D. Reactor Status
- Wenn Reactor im Fehlerstatus -> Task erzeugen

Bitte keine wilde DSL bauen.
Eine einfache, kontrollierte JSON-/Schema-basierte Konfiguration reicht.

---

## 5. Backend API

Implementiere mindestens:

### Rules
- GET /api/v1/rules
- GET /api/v1/rules/{id}
- POST /api/v1/rules
- PUT /api/v1/rules/{id}
- PATCH /api/v1/rules/{id}/enabled

### Rule execution
- POST /api/v1/rules/{id}/evaluate
  - optional dry_run=true/false

### Rule logs
- GET /api/v1/rules/{id}/executions
- optional GET /api/v1/rule-executions

Optional sinnvoll:
- POST /api/v1/rules/evaluate-all?dry_run=true

Wichtig:
- saubere Request-/Response-Schemas
- klare Fehlerantworten
- Rule-Konfiguration validieren
- Router schlank halten

---

## 6. Actions V1

Unterstützte Aktionen:

### create_alert
Mit konfigurierbaren Feldern wie:
- title template
- message template
- severity
- source_type
- source_id optional

### create_task
Mit konfigurierbaren Feldern wie:
- title template
- description template
- priority
- due_at offset optional
- charge_id/reactor_id optional wenn sauber ableitbar

Wichtig:
- keine Duplikats-Explosion erzeugen
- wenn sinnvoll kleine Schutzlogik gegen identische Wiederholungen einbauen
- aber V1 pragmatisch halten

---

## 7. Frontend

Baue neue Seite:

### /automation
oder
### /rules

Mit:
- Regelliste
- Regel anlegen
- Regel bearbeiten
- aktiv/inaktiv schalten
- dry-run / evaluate button
- Anzeige letzter Ausführungen
- Ergebnis sichtbar:
  - matched / not matched
  - action executed
  - error

UX:
- funktional
- erklärbar
- keine unnötige Design-Spielerei
- Regelkonfiguration lieber klar als hyper-generisch

---

## 8. Dashboard klein ergänzen

Wenn sinnvoll klein umsetzbar:
- Anzahl aktiver Regeln
- letzte Regelereignisse oder letzte Ausführungen

Dashboard nicht aufblasen.

---

## 9. Seed / Demo

Ergänze einige sinnvolle Demo-Regeln, z. B.:
- Temperatur zu hoch -> Alert
- pH zu niedrig -> Task
- Sensor ohne Werte 24h -> Alert
- überfällige Tasks -> Alert

Wichtig:
- Seed klein und nachvollziehbar
- keine riesige Demo-Magie

---

## 10. Tests

Ergänze sinnvolle Backend-Tests für:
- Regel anlegen
- Regel validieren
- dry-run evaluation
- echte execution
- create_alert action
- create_task action
- stale sensor case
- overdue tasks case
- execution log retrieval
- Migration darf nicht brechen

Bitte robust, aber pragmatisch.

---

## 11. Doku

Aktualisiere mindestens:
- README.md
- ROADMAP.md

Dokumentiere:
- welche Regeltypen unterstützt werden
- welche Actions unterstützt werden
- was dry_run bedeutet
- wie Regeln getestet werden
- wie die Engine bewusst begrenzt ist
- wie dieser Schritt als Grundlage für spätere Multi-Domain-Erweiterungen dient

---

# Wichtige Abgrenzung

NICHT in diesem Schritt:
- GPIO / Relais / Pumpensteuerung
- Hardware Actions
- Mail / SMS / Push Notifications
- Cron-/Scheduler-Cluster
- komplexe DSL
- Multi-Step Workflows
- autonome ABrain-Ausführung
- Vision-Regeln
- Wiki-RAG oder Wissensregeln
- Rollen/Auth
- AssetOps / InventoryOps / ITOps bereits implementieren

Nur:

eine nachvollziehbare, kontrollierte Regelengine V1 mit Task/Alert-Aktionen.

---

# Technische Leitlinien

- Pi-freundlich
- keine schweren neuen Libraries
- kleine Service-Schicht
- klare API-Struktur
- lieber wenige gute Regeltypen als halbfertige Universal-Engine
- nachvollziehbare Logs
- keine stille Automatik
- spätere Erweiterung auf weitere Domänen ermöglichen, aber in diesem Schritt nicht vorwegnehmen

---

# Arbeitsweise

1. Analyse aktueller Module und vorhandener Datenquellen/Zielobjekte.
2. Minimal sauberes Rule-Modell definieren.
3. Migration bauen.
4. Backend-Engine + API implementieren.
5. UI für Regeln und Dry-Run bauen.
6. Tests ergänzen.
7. Doku aktualisieren.

---

# Abschlussausgabe

Bitte liefern:

1. Welcher Schritt wurde umgesetzt?
2. Warum war das der richtige nächste Schritt?
3. Welche Dateien wurden geändert?
4. Was wurde konkret gebaut?
5. Welche Entscheidungen wurden getroffen?
6. Welche offenen Punkte bleiben?
7. Exakte lokale Test-/Start-/Migrationsbefehle
8. Passender Commit-Message-Vorschlag

Falls sinnvoll kleine Konsistenzverbesserungen im Scope durchführen.
