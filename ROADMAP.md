# ROADMAP

LabOS entwickelt sich zu einem modularen Operating System für EcoSphereLab.  
Der Fokus bleibt auf lokalem Betrieb, Raspberry-Pi-Tauglichkeit, klaren operativen Datenmodellen und kleinen nachvollziehbaren Erweiterungen. Die bestehende Ausrichtung bleibt erhalten und wird um eine stärkere Multi-Lab-, ReactorOps- und plattformorientierte Perspektive erweitert.

---

# Produktbild

LabOS ist nicht nur eine einzelne Labor-App, sondern das zentrale Betriebssystem für ein reales, hybrides Innovationslabor.

## Kernbereiche

- **BioOps**  
  Charges, Reaktoren, Kulturen, Sensorik, Fotos, Prozessdokumentation

- **ReactorOps**  
  Modulare Reaktorsysteme, Telemetrie, Setpoints, Schedules, Overrides, Kalibrierung, Safety, Digital Twin

- **MakerOps**  
  Werkbankgeräte, 3D-Druck, Elektronikgeräte, Fertigungsassets, Builds, Reparaturen

- **ITOps**  
  Server, SBCs, GPU-Nodes, Netzwerktechnik, Dienste, Storage, Backups

- **KnowledgeOps**  
  Wiki, SOPs, How-tos, Dev Docs, User Docs, verlinkbares Betriebswissen

- **Automation**  
  Regeln, Alerts, Tasks, nachvollziehbare Ausführungen, Dry-Runs

- **AI Assistenz**  
  LabOS ist **nicht selbst das Brain**. Ziel ist ein sauberes Andocken eines externen ABrain über eine MCP-/Tool-Adapter-Schicht; Smolit-AI-Assistant übernimmt die Nutzerkommunikation. Der bestehende lokale ABrain-Stub ist Übergangs-/Dev-Fallback, nicht Endzustand (siehe Zielarchitektur).

- **R&D Ops**  
  Projekte, Experimente, Hypothesen, Ergebnisse, Iterationen, Learnings

---

# Zielarchitektur

LabOS ist im Zielbild **Domain- und Tool-/State-System**, nicht Brain.

```text
Smolit-AI-Assistant  →  ABrain  →  LabOS MCP Server / Tool Adapter  →  LabOS API / DB
```

## Rollenverteilung

- **LabOS** = Domain-, Realitäts- und Tool-/State-System
  (ReactorOps, Telemetrie, Commands, Safety, Assets, Inventory, Vision, Scheduler, Operator-UI, lokale fachliche Guards)
- **ABrain** = Brain, Governance, Planning, Execution Control, Trace, Audit, agentische Orchestrierung
- **Smolit-AI-Assistant** = User-Interaktion, Sprache, UX, Chat

## Entscheidungsregel

- LabOS beschreibt und kontrolliert die Laborrealität.
- ABrain entscheidet, plant und regiert die Ausführung.
- Der Smolit-AI-Assistant spricht mit dem Menschen.

## Konsequenzen für diese Roadmap

- Die bestehende `ABrain Integration V1` in LabOS bleibt als **Übergangs- / Bridge- / Dev-Fallback-Schicht** erhalten, ist aber **nicht** der Endzustand.
- `ABrain V2` im Sinne dieser Roadmap bedeutet **nicht** einen intelligenteren internen LabOS-Assistenten, sondern einen sauberen Adapter nach außen: MCP-Server / Tool-Adapter, Context Builder, Action Catalog, Governance Boundary, Response- und Trace-Mapping.
- LabOS baut **kein** eigenes Planungs- oder Agenten-System und dupliziert **keine** ABrain-Governance oder Approval-Flows.
- Domain- und Safety-Guards (Kalibrierung, Safety-Incidents, Command-Guard) bleiben lokal in LabOS.

---

# Bereits umgesetzt

- Charges CRUD
- Reactors CRUD
- Alembic Migrationen
- Sensorik V1
- Tasks + Alerts V1
- Photo Upload + Vision Basis V1
- ABrain Integration V1 mit echtem LabOS-Kontext (Übergangs-/Bridge-Schicht, siehe Zielarchitektur)
- Regelengine / Automation V1
- AssetOps / DeviceOps V1
- Inventory / MaterialOps V1
- QR / Label / Traceability V1
- Rollen / Auth V1
- ReactorOps / Digital Twin V1
- Reactor Control / Telemetry V1
- MQTT / ESP32 / Pi Architektur V1
- **Calibration / Maintenance / Safety V1**
- **Command ACK / Retry V1**
- **Scheduler / Automation Runtime V1**
- **Vision Node / AI Integration V1**
- **Sensor + Vision Fusion / Reactor Health V1**
- **ABrain Adapter Alignment V1 (Phase 1+2+3)**
- **Boundary Hardening V1**
- **Approval System V1 (HITL + Queue + UI + Audit)**
- Dashboard-Basis
- Wiki-Basis

---

# Aktueller Status: Sensor + Vision Fusion / Reactor Health V1

Mit diesem Schritt bekommt LabOS eine deterministische Reactor-Health-Ebene, die Telemetrie, Vision-Auswertung und Safety-Zustand zu einem strukturierten Statuswert pro Reaktor fusioniert.

## Enthalten

- `ReactorHealthAssessment`-Modell (`reactor_id`, `status`, `summary`, `signals` JSON-Array, `source_telemetry_at`, `source_vision_analysis_id`, `source_incident_count`, `assessed_at`, `created_at`) mit Migration `20260419_0017`
- Statuswerte: `nominal`, `attention`, `warning`, `incident`, `unknown`
- Fusion-Service `services/api/app/services/reactor_health.py` liest neueste Telemetrie je Sensor-Typ, letzte erfolgreiche `VisionAnalysis`, offene `SafetyIncident`s und `ReactorTwin`/`ReactorSetpoint`-Zielbereiche
- deterministische Regeln: Telemetrie fehlend/veraltet/out-of-range/nominal, Vision-Kontaminationsverdacht/Helligkeitsprobleme/Gruenanteil/Low-Sharpness/Low-Confidence, Safety critical/high/warning/info
- Statusableitung `incident > warning > attention > nominal`; `unknown` nur wenn gar keine Daten vorliegen
- API: `GET /api/v1/reactor-health`, `GET /api/v1/reactor-health/{id}`, `GET /api/v1/reactor-health/{id}/history`, `POST /api/v1/reactor-health/{id}/assess` (Operator)
- `ReactorTwinRead` liefert `latest_health` mit Summary und Signalen
- ABrain-Kontext-Section `reactors` enthaelt `health_status`, `health_summary`, `health_assessed_at`; Sortierung priorisiert `incident > warning > attention > unknown > nominal`
- Dashboard-KPIs: `reactors_health_nominal/attention/warning/incident/unknown`
- Auto-Trigger nach Photo-Upload mit Reaktor-Bezug (best-effort)
- `/reactor-ops`-Frontend mit Health-Badge in Tabelle, Detail-Card mit Summary + Signal-Liste und "Neu bewerten"-Button
- Dashboard zeigt Reactor-Health-KPI-Reihe (Nominal, Auffaellig/Warnung, Incident)
- Seed: 4 Demo-Bewertungen (nominal A1, attention B1 via Vision, warning C1 via Telemetrie+Vision, incident D1 via Safety)
- 8 neue Backend-Tests (nominal, attention-by-vision, warning-by-telemetry+vision, incident-by-safety, unknown, list/history, count_by_status, ReactorTwin-Integration)

## Bewusst noch nicht enthalten

- ML-Modelle, Zeitreihen-Analyse, Trend-/Vorhersage
- automatische Steuerungseingriffe basierend auf Health-Status
- Aggregation ueber mehrere Reaktoren / Zonen oder Lab-weite Gesundheitsindizes
- eigener Health-Scheduler (noch ueber Vision-Auto-Trigger und manuelles Reassess)

## Grundlage fuer

- automatische Alerts bei Warning/Incident-Status
- Scheduler-basierte zyklische Reassess-Runs
- Health-gestuetzte Safety-Gates fuer Reactor-Commands
- Health-Trends ueber Zeit in Dashboard und ABrain

---

# Aktueller Status: Vision Node / AI Integration V1

Mit diesem Schritt bekommt LabOS eine lokale, ML-freie Bildanalyse: jedes hochgeladene Foto wird automatisch ausgewertet und die Ergebnisse stehen in Photo-UI, ReactorOps-Twin und ABrain zur Verfuegung.

## Enthalten

- `VisionAnalysis`-Modell (`photo_id`, `reactor_id`, `analysis_type`, `status`, `result` JSON, `confidence`, `error`, `created_at`) mit Migration `20260419_0016`
- `services/api/app/services/vision.py` liefert Pillow-basierten `analyze_image` mit Aufloesung, Durchschnitts- und Streuungs-RGB, Helligkeit, Schaerfe, dominanter Farbe, Gruen-/Braun-Anteil
- regelbasierte Klassifikation `health_label`: `healthy_green`, `growing`, `low_biomass`, `no_growth_visible`, `contamination_suspected`, `too_dark`, `overexposed`
- Konfidenz aus Kontrast, Schaerfe und Signalanteil (0-1)
- Auto-Analyse nach `POST /api/v1/photos/upload`, Fehler werden als `status='failed'` persistiert ohne den Upload zu blockieren
- API: `GET /api/v1/vision/photos/{id}`, `GET /api/v1/vision/photos/{id}/history`, `POST /api/v1/vision/analyze/{id}` (Operator)
- `PhotoRead`, `PhotoAnalysisStatusRead` und `ReactorTwinRead` liefern `latest_vision`
- ABrain-Kontext-Section `photos` traegt `vision_health_label`, `vision_green_ratio`, `vision_brown_ratio`, `vision_confidence`
- `/photos`-Frontend zeigt Health-Badge je Kachel und eine Detailauswertung (Klassifikation, Konfidenz, Helligkeit, Schaerfe, Gruen-/Braun-Anteil, Ø- und dominante Farbe als Swatch) plus einen "Neu analysieren"-Button
- 8 neue Backend-Tests fuer Auto-Analyse, History, Re-Analyse, Dunkel-/Kontaminations-Klassifikation, Reactor-Twin- und ABrain-Integration

## Bewusst noch nicht enthalten

- neuronale Modelle (torch, tensorflow, opencv-dnn) oder Objekt-/Segmentierung
- GPU-/Jetson-Integration
- mehrstufige Pipelines, Zeitreihen-Vergleiche oder automatische Alerts auf Vision-Ergebnissen
- Vision-Triggerung ueber den Scheduler / MQTT-Node-Kommandos

## Grundlage fuer

- Vision V2 mit modellbasierter Klassifikation / Segmentation
- automatische Alerts bei Kontaminationsverdacht oder Helligkeitsproblemen
- ABrain-Hinweise und Empfehlungen auf Basis echter Bildmetriken
- Kopplung mit Scheduler (`sample_capture`) fuer tagesaktuelle Bild-Vergleiche

---

# Aktueller Status: Scheduler / Automation Runtime V1

Mit diesem Schritt bekommt LabOS eine eigene leichte Automation-Runtime: Reactor-Commands und Rule-Checks koennen zeitbasiert (interval/cron) oder manuell ausgefuehrt werden, ohne externen Scheduler.

## Enthalten

- `Schedule`-Modell mit `schedule_type` (`interval`/`cron`/`manual`), `target_type` (`command`/`rule`), `target_params` (JSON), `reactor_id`, `target_id`, `last_run_at`, `next_run_at`, `last_status`, `last_error`
- `ScheduleExecution`-Log mit `status`, `trigger`, Start-/Finish-Timestamps, Ergebnis-JSON und Fehlertext
- `SchedulerRunner` als Daemon-Thread im FastAPI-Lifespan, Tick alle 5 s, per `scheduler_enabled` abschaltbar
- eigener 5-Feld-Cron-Parser (Minute/Stunde/Tag/Monat/Wochentag, `*`, `*/N`, Ranges, Listen)
- API: `GET/POST /api/v1/schedules`, `PATCH /api/v1/schedules/{id}`, `PATCH /api/v1/schedules/{id}/enabled`, `DELETE /api/v1/schedules/{id}`, `GET /api/v1/schedules/{id}/executions`, `POST /api/v1/schedules/{id}/run`
- Writes sind Operator/Admin, Reads authenticated
- Command-Schedules nutzen den bestehenden Safety-Guard-Pfad aus Command ACK/Retry
- Frontend `/schedules` mit Formular, Tabelle, Enable/Disable, Manuell-Run und Ausfuehrungshistorie
- Seed: vier Beispiel-Schedules (Lichtzyklus, Rule-Check 60 s, Sample-Capture 5 min, Wartungscheck cron), initial deaktiviert
- 13 neue Backend-Tests (Cron-Parser, Payload-Validierung, CRUD, Enabled-Toggle, Manual-Run, Due-Detection, Execute-Failure, Tick, Executions-Endpoint, RBAC, Cron-Validierung, Delete)

## Bewusst noch nicht enthalten

- parallele Worker oder verteilter Scheduler (Celery/k8s CronJob/DAG)
- Nicknames wie `@hourly`, Sekunden-Granularitaet oder erweiterte Cron-Syntax (`L`, `W`, `#`)
- ueberschlagender Retry-Controller fuer fehlgeschlagene Schedule-Runs
- eigene Scheduler-Metriken / Prometheus-Export

## Grundlage fuer

- geschlossene Regelkreise mit Zeitfenstern (Licht an/aus ueber Tag)
- regelmaessige Sampling-Pipelines (Vision, Telemetrie)
- wiederkehrende Wartungs- und Kalibrierpruefungen
- kombinierte Scheduler-/Rule-Engine mit ACK-Feedback

---

# Aktueller Status: Command ACK / Retry V1

Mit diesem Schritt werden MQTT-Commands nicht nur versendet, sondern auch nachverfolgbar bestaetigt, beim Ausbleiben einer Antwort markiert und auf Operator-Anforderung wiederholt.

## Enthalten

- `ReactorCommand.command_uid` als stabile UUID fuer MQTT/Node-Korrelation
- neue Felder `published_at`, `acknowledged_at`, `timeout_at`, `retry_count`, `max_retries`, `last_error`, `ack_payload`
- Status-Erweiterung: `acknowledged`, `timeout`, `retrying`
- Publish-Payload enthaelt `command_uid`; ACK-Topic `labos/reactor/{id}/ack`
- MQTT-Bridge abonniert ACK-Topic, validiert Payload und setzt Status auf `acknowledged` bzw. `failed`
- Retry-Endpoint `POST /api/v1/reactor-commands/{id}/retry` (inkrementiert `retry_count`, respektiert `max_retries`, lehnt bereits bestaetigte/blockierte Commands ab)
- Timeout-Endpoint `POST /api/v1/reactor-commands/check-timeouts` (pragmatischer manueller Check, kein Background-Scheduler)
- Frontend zeigt ACK-Status, Retry-Zaehler, Fehler und Retry-Button in der Command-Tabelle
- Simulator (`scripts/mqtt/simulate_env_node.py`) und ESP32-Beispiel senden ACKs zurueck, Simulator mit optionalem `--ack-error-rate`
- 8 neue Backend-Tests fuer ACK-Topic-Parsing, Bridge-Handler, Timeout-Transition und Retry-Endpoint

## Bewusst noch nicht enthalten

- automatischer Retry-Scheduler / Background-Worker
- QoS 1/2 oder Retained-ACKs
- Audit-Trail-Export fuer Commands
- Multi-Broker / Broker-Failover
- Hardware-echtes Interlock beim Retry

## Grundlage fuer

- automatischer Scheduler (Licht, Pumpe, Aeration) mit ACK-Feedback
- Dosing-Workflows mit Bestaetigungskette
- Event-basierte Alerting-Regeln auf `timeout`/`failed`-Commands
- Vision-/Sensor-Kommandos mit Node-Rueckmeldung

---

# Aktueller Status: Calibration / Maintenance / Safety V1

Dieser Schritt gibt LabOS erstmals eine saubere betriebliche Sicherheits- und Vertrauensebene fuer Reaktoren, Sensoren und Nodes.

## Enthalten

- `CalibrationRecord` fuer pH, Temp, EC, Flow und andere Parameter auf Reaktoren, Nodes und Assets
- `MaintenanceRecord` fuer Reinigung, Inspektion, Austausch und Service
- `SafetyIncident` mit Typen, Schweregraden, Statuswechsel und optionalem Reaktor-/Node-Bezug
- Command-Guard-Logik: Commands werden geblockt, wenn kritische Incidents offen sind, Nodes offline sind oder Kalibrierungen abgelaufen sind
- `blocked_reason` als erklaerbares Protokollfeld am ReactorCommand
- Dashboard-KPIs: offene Incidents, faellige Kalibrierungen, ueberfaellige Wartung
- Safety-Seite `/safety` mit Incident-, Kalibrierungs- und Wartungsansicht
- Seed-Daten fuer nachvollziehbare Demo-Szenarien
- 25 Backend-Tests fuer alle neuen Endpunkte und Guard-Logik

## Verhaeltnis zu ReactorOps / Reactor Control

- ReactorOps (Digital Twin, Setpoints, Events) bleibt unveraendert
- Commands nutzen jetzt die Guard-Schicht vor dem MQTT-Publish
- Incidents koennen sich auf Reaktor-ID oder DeviceNode-ID beziehen
- Kalibrierung und Wartung sind Ziel-ID-basiert, nicht im Digital Twin modelliert

## Bewusst noch nicht enthalten

- echte Hardware-Abschaltung / GPIO-Safe-State
- ACK / Retry fuer Commands
- PID / Control Loops
- automatische Kalibrierworkflows
- MQTT-Haertung / TLS
- vollautomatische Safety-Steuerung
- Compliance-/Audit-Framework

## Grundlage fuer

- Command ACK / Retry mit Guard-Pre-Check
- Scheduler mit Guard-Bedingungen
- Vision Node
- echte Hardware-Kommandos mit Safety-Gate
- geschlossene Regelkreise mit Interlock-Bedingungen

---

# Aktueller Status: MQTT / ESP32 / Pi Architektur V1

Der aktuelle Schritt erweitert LabOS von reiner REST-basierter Reactor-Control-Struktur zu einer echten lokalen Messaging- und Node-Anbindungsschicht fuer Pi- und ESP32-nahe Betriebsablaeufe.

## Enthalten

- lokaler Mosquitto-Broker im Compose-Stack
- definierte Topic-Struktur fuer Reaktor-Telemetrie, Control, Node-Status und Heartbeats
- Python-MQTT-Bridge im API-Service mit sauberem Startup-/Shutdown-Hook
- Persistierung von MQTT-Telemetrie in `TelemetryValue`
- Upsert von Node-Status/Heartbeats in `DeviceNode`
- optionaler MQTT-Publish fuer `ReactorCommand`
- `node_id` als minimale stabile Node-Identitaet fuer DeviceNodes
- kleine UI-Sichtbarkeit fuer MQTT-Bridge-Status, Device-Node-ID und Device-originierte Telemetrie
- Beispiel-Firmware und lokaler MQTT-Simulator fuer testbare Dev-Pfade

## Bewusst noch nicht enthalten

- MQTT-Auth/TLS-Haertung
- WebSocket-Live-UI
- GPIO-, Serial- oder Firmware-Aufrufe mit echter Anlagenwirkung
- ACK / Retry
- Licht-/Temperatur-Scheduler
- Dosing- und PID-Logik
- Kalibrier-Workflows als eigenes Modul
- Safety-/Interlock-Systeme
- Incident-Automation
- Multi-Reactor-Orchestrierung

---

# Strategische Ausrichtung ab jetzt

LabOS wird schrittweise vom operativen Kern zu einem vollständigen EcoSphereLab OS erweitert.

Das bedeutet:

- reale Geräte + reale Materialien + reale Prozesse + reales Wissen
- nicht nur Dokumentation, sondern Betriebsführung
- nicht nur Bio-Lab, sondern Multi-Domain-Lab
- nicht nur Dashboards, sondern Handlungssystem
- nicht nur Daten sammeln, sondern strukturieren, steuern und verbessern

---

# Priorisierte nächste Schritte

## Priorität A – Operativer Kern

1. Inventur- / Scan-Workflow V1 vervollstaendigen
2. Asset-nahe Wartungslogik mit Alerts und Regeln
3. Verbrauchshistorie / Nachkauf-Vorbereitung auf Basis des Inventory- und Label-Modells
4. Rollen / Auth V1 zu feineren Berechtigungen, Safety-Guards und spaeterem Audit-Ausbau vorbereiten
5. MQTT-/Node-Layer an ACK, Retry, Device-Health und spaetere Safety-Guards anschlussfaehig vertiefen

---

## Priorität B – ReactorOps Ausbau

5. ReactorOps / Digital Twin V1 ✓
6. Reactor Control / Telemetry V1 ✓
7. Calibration / Maintenance / Safety V1 ✓
8. Command ACK / Retry V1 ✓
9. Scheduler / Automation Runtime V1 ✓
10. Vision Node / AI Integration V1 ✓
11. Sensor + Vision Fusion / Reactor Health V1 ✓
12. ABrain Adapter Alignment V1 ✓ (Phase 1: Context Builder, Action Catalog, Adapter-Orchestrator, Governance-Boundary, Response/Trace Mapping; Phase 2: Legacy-Endpoints `/api/v1/abrain/status|query` delegieren jetzt als Thin Adapter an `abrain_adapter`, keine eigene Reasoning-Logik mehr in `services/abrain.py`; Phase 3: Execution + Governance Flow — static `ACTION_MAP`, Role-/Approval-/Safety-Guards, `ABrainExecutionLog`, `POST /api/v1/abrain/execute`, vollständige Trace-Protokollierung)
13. Boundary Hardening V1 ✓ (harte Trennung LabOS vs. ABrain: Signal-statt-Entscheidung-Prinzip, Rule Engine als Local-Automation-Fallback markiert, Scheduler auf Execution-Only beschränkt, Reactor-Health/Vision als Classification + Signals, Safety als einzige Blocker-Autorität mit `safety_guard:`-Prefix, ABrain-Stub klar als Dev-Fallback gekennzeichnet)
14. Approval System V1 ✓ (HITL-Queue + State + UI + Audit für approval-pflichtige ABrain-Aktionen: `ApprovalRequest`-Modell + Migration 0019, `services/approvals.py`, Integration in `abrain_execution` für `pending_approval`-Flow, `POST /api/v1/approvals/{id}/approve|reject` mit Rollenlogik (viewer read / operator low+medium / admin inkl. high+critical), Re-Apply von Safety- und Rollen-Guards bei Ausführung via bestehenden `execute_action`-Pfad, `/approvals`-Operator-UI mit Overview, Filter, Detail, Decision-Note; Approval ist release, nicht bypass)

---

## Priorität C – EcoSphereLab Ausbau

8. ITOps / InfraOps V1
9. Sensorik V2 mit Asset- und Device-Bezug
10. Wiki-UI V2 mit tieferen Referenzen zwischen Objekten und Dokumenten
11. Experiments / R&D Ops V1

---

## Priorität D – Intelligence Layer

12. **ABrain Adapter Alignment V1** (MCP / Tool Adapter, Context Builder, Action Catalog, Governance Boundary, Response/Trace Mapping — siehe [ABrain Roadmap](#abrain-roadmap))
13. Vision V2 für strukturierte Foto-Auswertung
14. **ABrain V2 Domain Reasoning** (Reactor Intelligence, Daily Ops, Incident Review, Maintenance Suggestions, Cross-Domain Reasoning — Reasoning liegt im externen ABrain, nicht in LabOS)
15. Predictive / Recommendation Features

---

## Priorität E – Skalierung

15. Multi-Node / Zone-Awareness V1
16. Backup / Restore / Deployment Härtung
17. Pilotnutzung außerhalb des eigenen Labs

---

# Geplante Ausbauphasen

---

## v0.2.x – Operativ starkes LabOS

Ziel:

- Geräte und Materialien integriert
- QR-fähige reale Objekte
- Rollenmodell und lokale Auth-Basis
- ReactorOps-Grundlage mit Digital Twin
- Reactor-Control-Basis mit Telemetrie, Setpoints und Devices
- MQTT-Basis fuer ESP32-/Pi-Nodes
- Wartungslogik
- erste ReactorOps-Strukturen

---

## v0.3.x – Smart LabOS

Ziel:

- Digital Twin für Reaktoren
- modulare Telemetrie
- Kalibrier- und Safety-Logik
- Cross-Domain Assistenz
- Vision-Auswertung

---

## v0.4.x – EcoSphereLab OS

Ziel:

- BioOps + ReactorOps + MakerOps + ITOps + KnowledgeOps in einem System
- mehrere Zonen / mehrere Nodes
- strukturierte Automation
- Assistenz auf Systemebene
- echtes Betriebs- und Wissenssystem

---

# ReactorOps Roadmap (neu integriert)

ALG-1-artige Systeme dienen als Inspirationsquelle für Funktionsklassen – nicht als Kopiervorlage.

LabOS übernimmt diese Fähigkeiten als Plattformmodule.

---

## ReactorOps / Digital Twin V1

Ein Reaktor wird nicht nur Stammdatensatz, sondern Prozessobjekt.

### Enthalten:

- Kulturtyp / Strain
- Volumen
- Medium / Rezept
- Inokulationsdatum
- Zielbereiche für pH / Temperatur / Licht / Flow
- Wachstumsphase
- Erntefenster
- letzte Eingriffe
- Kontaminationsereignisse
- Prozesshistorie

---

## Reactor Control / Telemetry V1

### Enthalten:

- Telemetriekanäle:
  - pH
  - Temperatur
  - Licht
  - Flow
- Setpoints
- Device- / Node-Struktur
- Command-Log / Stub-Queue
- API fuer Ingest, Latest und History
- vorbereitete spaetere ACK-/Command-Pipeline
- einfache UI fuer Werte, Setpoints und Commands

---

## MQTT / ESP32 / Pi Architektur V1

### Enthalten:

- lokaler Mosquitto-Broker
- Topic-Schema fuer:
  - Telemetrie
  - Control
  - Status
  - Heartbeat
- Python-Bridge von MQTT nach LabOS-Modell
- vorbereiteter Command-Publish von LabOS nach MQTT
- minimale Node-Identitaet mit `node_id`
- ESP32-Referenz und lokaler Simulationspfad

---

## Calibration / Maintenance / Safety V1

### Enthalten:

- Kalibrierstatus
- Kalibrierintervalle
- Wartung fällig
- Incident-Typen:
  - clogging suspicion
  - dry run risk
  - overheat
  - module fault
- Safe-State Konzepte
- automatische Wartungs-Tasks

---

# Inventory / MaterialOps Roadmap

## Bereits in V1 umgesetzt

- Materialien
- Verbrauchsgüter
- Mengen / Einheiten
- Lagerorte
- Mindestbestände
- kritische Bestände
- Asset-Zuordnung optional

## Als nächste Ausbaustufen

- Verbrauchshistorie
- Einkaufslisten
- Lieferanten
- Batch-/Lot-Tracking

---

# QR / Label / Traceability Roadmap

## Bereits in V1 umgesetzt

- Label-Codes für reale Objekte
- QR-Ziele für Assets und Inventory
- scan-fähige Browser-Zielseite
- Aktiv/Inaktiv-Status für Labels
- kleine Dashboard- und Objekt-Integration

## Als nächste Ausbaustufen

- mobile Scan-optimierte Flows
- Inventur-Unterstützung
- Zone- / Shelf- / Box-Labels
- Reactor-, Charge- und Experiment-Ziele
- Reprints / Label-Historie

---

# ITOps Roadmap

## ITOps / InfraOps V1

- Hosts
- Nodes
- Dienste
- Storage
- Backupstatus
- Rollen
- operative IT-Aufgaben

## Später:

- Container Health
- GPU Jobs
- Netzwerkdiagramme
- Auto Discovery

---

# KnowledgeOps Roadmap

## Wiki V2

- tiefe Objektverknüpfungen
- Asset ↔ SOP
- Reactor ↔ Rezept
- Task ↔ Anleitung
- Experiment ↔ Ergebnis
- Suchbarkeit verbessern

---

# ABrain Roadmap

> Zielbild (siehe [Zielarchitektur](#zielarchitektur)):
> `Smolit-AI-Assistant → ABrain → LabOS MCP / Tool Adapter → LabOS API / DB`.
> LabOS liefert Domain-State, Aktionen und Guards; ABrain liefert Planung, Governance und Reasoning. Der bestehende lokale `/api/v1/abrain/*`-Stub bleibt Übergangsschicht.

## ABrain Adapter Alignment V1 (Phase 1 + Phase 2 + Phase 3 abgeschlossen)

Ziel: LabOS wird sauber andockbar für ein externes ABrain. Diese Phase ist **keine Feature-Erweiterung der internen Assistenzlogik**, sondern der Umbau zum Adapter.

Phase 1 liefert:

- Context Builder als `app/services/abrain_context.py` (Reactor-, Operations-, Resource-, Schedule-Context, vertraglich über `ABrainAdapterContextRead`).
- Statischer Action Catalog in `app/services/abrain_actions.py` (9 kuratierte Aktionen mit Risk/Approval/Allowed-Roles/Guards).
- Thin HTTP Client `app/services/abrain_client.py` gegen externes ABrain (mit Timeout, Enable, Mode).
- Adapter-Orchestrator `app/services/abrain_adapter.py` mit Response/Trace Mapping, Approval-/Blocked-Actions und lokalem Fallback (`policy_decision=local_rules_v1`).
- Router-Ergänzung `/api/v1/abrain/actions`, `/api/v1/abrain/adapter/context`, `/api/v1/abrain/adapter/query` (Admin-only für `adapter/query`).
- Frontend-Console `ABrainAdapterConsole` auf `/abrain` mit Modus-Anzeige, Tool-Surface-Preview, Trace-ID und Risk/Approval-Badges.
- Neue Settings: `ABRAIN_ENABLED`, `ABRAIN_MODE`, `ABRAIN_USE_LOCAL_FALLBACK`, `ABRAIN_ADAPTER_CONTRACT_VERSION`.

Phase 2 liefert (Thin Adapter Routing):

- `services/abrain.py` ist reine Legacy-Facade ohne eigene Reasoning-/Fallback-Logik. `get_status()` und `query()` delegieren an `abrain_adapter`.
- `/api/v1/abrain/status` und `/api/v1/abrain/query` nutzen dieselbe Context-, Catalog- und Governance-Kette wie `/adapter/*`.
- Adapter-Modus `local` wird für das Legacy-Schema als `stub` zurückgemeldet, damit die bestehende UI kompatibel bleibt.
- Direkter HTTP-Client-Aufruf aus `services/abrain.py` wurde entfernt; einziger HTTP-Pfad nach ABrain ist jetzt `abrain_client.py`.
- Neuer Test `test_legacy_query_delegates_through_adapter` verifiziert den Adapter-Pfad der Legacy-Route.

Phase 3 liefert (Execution + Governance Flow):

- `services/abrain_execution.py` mit **statischem `ACTION_MAP`** (`labos.create_task`, `labos.create_alert`, `labos.create_reactor_command`, `labos.retry_reactor_command`, `labos.ack_safety_incident`). Kein Dynamic Dispatch, kein Reflection, keine neuen Actions ohne Code-Review.
- Execution-Pipeline: Catalog-Lookup → Role-Check gegen `descriptor.allowed_roles` → Approval-Gate (`requires_approval` ohne `approve=True` → `pending_approval`) → Dispatch an bestehende Service-Layer → Ergebnis-Normalisierung → Log.
- Safety-Guard: Reactor-Commands delegieren an `reactor_control.create_reactor_command`, das lokal `safety_service.check_command_guards` ruft. Ein `status='blocked'`-Ergebnis wird als `ABrainExecutionStatus.blocked` mit `blocked_reason='safety_guard: …'` protokolliert.
- Neues Modell `ABrainExecutionLog` (Migration `20260419_0018`) mit `action`, `params`, `status`, `blocked_reason`, `executed_by`, `trace_id`, `source`, `result`, `created_at` und Indizes auf `action`, `status`, `trace_id`, `created_at`.
- Neuer Endpoint `POST /api/v1/abrain/execute` (Role-Check passiert im Service via Katalog, nicht am Router) mit Rückgabe `ABrainExecutionResult`.
- Neue Schemas `ABrainExecuteRequest`, `ABrainExecutionResult`, `ABrainExecutionStatus`, `ABrainExecutionLogRead`.
- Governance-Regel: Reasoning-, Fallback- und Policy-Entscheidungen bleiben im Adapter. `abrain_execution` ist reiner Enforcement- und Audit-Pfad — kein Planning, kein Dynamic Routing.

Noch offen (bewusst außerhalb Phase 1/2/3):

- Vollwertiger MCP-Server (aktuell nur HTTP-Adapter-Endpunkte).
- Externe Execution-Control / Approval-Pfad durch ABrain selbst (LabOS gated aktuell über `approve`-Flag im Request; der Workflow drumherum gehört in ABrain bzw. Smolit).
- Rückkopplung externer Actions über den Adapter auf LabOS-Commands und -Events.
- UI-Surface für `ABrainExecutionLog` (Historie, Filter nach `trace_id`/`status`).
- Erweiterung `ACTION_MAP` um `run_reactor_health_assessment`, `create_maintenance_record`, `create_calibration_record`, `run_schedule_now` (Katalog ist bereits vorhanden, nur Mapping fehlt).

Bausteine:

- **Context Builder**
  - strukturierte LabOS-Sicht für ABrain: Reaktoren (inkl. Reactor Health), Safety, Telemetrie, Vision, Tasks, Alerts, Inventory, Assets, Scheduler
  - stabile Schemas, klare Section-Keys, zeitliche Bezugspunkte
- **Action Catalog / Tool Surface**
  - kuratierte Liste der von außen aufrufbaren LabOS-Aktionen
  - z.B. Reactor-Command queueen, Reactor-Health neu bewerten, Task anlegen, Alert anlegen, Inventory-Status setzen, Schedule an-/ausschalten
  - jede Aktion mit Zweck, Parametern, Rolle, Seiteneffekten
- **MCP Server oder Tool Adapter**
  - eine saubere technische Andockschicht, über die ABrain Kontext lesen und Actions auslösen kann
  - kein agentisches Verhalten in LabOS selbst
- **Governance Boundary**
  - LabOS validiert, führt aus und protokolliert, plant aber nicht
  - ABrain ist für Planung, Approval, Execution Control und Audit zuständig
  - lokale Safety-/Domain-Guards (Kalibrierung, Safety-Incidents, Command-Guard) bleiben in LabOS und sind auch für extern initiierte Aktionen verbindlich
- **Response / Trace Mapping**
  - ABrain-Antworten und -Entscheidungen werden auf LabOS-Events, -Tasks oder -Commands gemappt
  - jede extern ausgelöste Aktion bleibt in LabOS nachvollziehbar (wer, wann, welche Aktion, welches Ergebnis)
- **Lokaler Dev-Fallback**
  - der bestehende Stub bleibt nur als optionaler, sekundärer Pfad für Offline- und Dev-Betrieb erhalten
  - er wird nicht weiter zu einem „smarten internen Assistent" ausgebaut

## ABrain V2 Domain Reasoning (Folgephase)

Baut auf Adapter Alignment V1 auf. Das eigentliche Reasoning passiert **im externen ABrain**, nicht in LabOS. LabOS liefert dafür Daten, Aktionen und Guardrails.

Themenfelder:

- **Reactor Intelligence** – Trends in Reactor Health, Telemetrie und Vision, frühe Warnsignale
- **Daily Ops** – Tagesplanung, Routinen, operative Vorschläge auf Basis offener Tasks/Alerts
- **Incident Review** – Ursachenanalyse für Safety-Incidents und Command-Fails mit Bezug auf Historie
- **Maintenance Suggestions** – Wartungs-/Kalibriervorschläge aus CalibrationRecord / MaintenanceRecord / Asset-Historie
- **Cross-Domain Reasoning** – BioOps + ReactorOps + MakerOps + ITOps + KnowledgeOps gemeinsam betrachten

## Später

- aktive Assistenz (ABrain-initiiert, über den Adapter)
- Voice Layer (über Smolit-AI-Assistant)
- Multi-Agent Flows (orchestriert in ABrain, ausgeführt gegen LabOS-Actions)

---

# Architekturleitlinien

- modularer Monolith vor Service-Aufspaltung
- lokale Datenhaltung vor Cloud-Annahmen
- wenige klare Modelle statt generischer Meta-Systeme
- Erweiterungen entlang realer Betriebsobjekte
- Cross-Domain-Verknüpfungen explizit und nachvollziehbar halten
- Pi-Tauglichkeit bleibt Pflicht
- Safety vor Spielerei
- echte Nutzung vor theoretischer Architektur

---

# Wichtige Abgrenzungen

- Assets / Devices sind nicht dasselbe wie Inventory
- Reaktoren sind nicht nur Assets, sondern Prozesssysteme
- LabOS ist **nicht** das Brain; ABrain übernimmt Planung und Governance, LabOS liefert Domain-State und Actions über einen MCP-/Tool-Adapter
- der lokale ABrain-Stub ist Übergangs-/Dev-Fallback, kein Endzustand
- Smolit-AI-Assistant ist die User-/Chat-Ebene, nicht LabOS selbst
- Automatisierung muss sichtbar, protokolliert und deaktivierbar bleiben
- Vision ersetzt keine saubere Sensorik
- jede Erweiterung muss für Raspberry Pi 4/5 praktikabel bleiben

---

# Technische Leitlinien

## Frontend

- einfache nutzbare Operator-UIs
- klare Dashboards
- mobile / Touchscreen brauchbar
- keine unnötig schwere UI-Komplexität

## Backend

- Services statt fette Router
- klare Schemas
- Alembic-first
- nachvollziehbare APIs
- Rule Engine ausbaubar halten

## Datenbank

- saubere Kernobjekte
- Indizes
- Historisierung
- Zustände explizit modellieren
- keine chaotischen Freitext-Silos

---

# Risiken

## Produkt-Risiken

- zu viele Domänen parallel
- Feature-Wildwuchs
- zu wenig echter täglicher Nutzen
- LabOS bleibt zu abstrakt

## Technische Risiken

- zu schwere Stacks für Pi
- Datenmodell driftet
- UI inkonsistent
- zu frühe Komplexität

## Gegenmaßnahmen

- kleine reale Inkremente
- jede Woche nutzbarer Fortschritt
- echte Nutzung priorisieren
- konsequentes Scope-Management

---

# Definition of Done

Ein Feature gilt als fertig, wenn:

1. Code implementiert ist
2. UI oder API sinnvoll nutzbar ist
3. Fehlerfälle berücksichtigt sind
4. Tests ergänzt wurden
5. Doku aktualisiert wurde
6. Docker/dev Setup funktioniert
7. Raspberry-Pi-Tauglichkeit mitgedacht wurde
8. Das Feature ins Gesamtmodell passt

---

# Langfristige Vision

LabOS wird das zentrale Operating System eines unabhängigen Innovationslabors.

Später möglich:

- mehrere Standorte
- mehrere Pis / Nodes
- modulare Reaktorfamilien
- Asset + Inventory + Produktion
- Vision + Assistenz + Analytics
- SOP-gesteuerte Prozesse
- digitale Laborzwillinge
- reale Pilotnutzung durch Dritte
- Produktisierung als Plattform
