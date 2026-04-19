# LabOS

LabOS ist ein Raspberry-Pi-taugliches Operating System fuer EcoSphereLab. Es verbindet BioOps, MakerOps, ITOps, R&D Ops, KnowledgeOps, Automation und AI-Assistenz in einem lokal betreibbaren modularen Monolithen.

## V1 Scope

- Dashboard
- Chargenverwaltung mit Create/Edit/Statuswechsel
- Reaktorverwaltung mit Create/Edit/Statuswechsel
- AssetOps / DeviceOps V1 mit CRUD, Wartungsfeldern und operativen Verknuepfungen
- Inventory / MaterialOps V1 mit Bestandsfeldern, Lagerorten und Mindestbestaenden
- QR / Label / Traceability V1 mit scan-faehigen Objekt-Links
- Rollen / Auth V1 mit lokalen Benutzerkonten, Login und API-Schutz
- ReactorOps / Digital Twin V1 mit Betriebszustand, Zielbereichen und Event-Historie pro Reaktor
- Reactor Control / Telemetry V1 mit Zeitreihen, Setpoints, Devices und Command-Stub-Queue
- MQTT / ESP32 / Pi Architektur V1 mit lokalem Broker, Topic-Struktur und Bridge-Schicht
- Sensorik V1 mit CRUD, Werte-Ingest und Verlauf
- Tasks + Alerts V1 mit operativen Dashboards
- Foto Upload + Vision Basis V1
- ABrain Integration V1 mit echtem LabOS-Kontext
- Regelengine / Automation V1
- **Calibration / Maintenance / Safety V1** mit Kalibrierstatus, Wartungserfassung, Incident-Tracking und Command-Guards
- **Command ACK / Retry V1** mit Command-UID, MQTT-ACK-Topics, Zustell-/Timeout-Tracking und manuellem Retry
- **Scheduler / Automation Runtime V1** mit interval/cron/manual-Schedules, Hintergrund-Runner und Ausfuehrungslog
- integriertes Wiki auf Markdown-Basis
- Docker-Compose-Setup für lokale Entwicklung

## Calibration / Maintenance / Safety V1

Diese Schicht schafft die Sicherheits- und Betriebsgrundlage fuer reaktornahe Steuerung.

### Was enthalten ist

**Kalibrierung (`CalibrationRecord`)**
- Kalibrierzustaende: `valid`, `due`, `expired`, `failed`, `unknown`
- Zieltypen: `reactor`, `device_node`, `asset`
- Parameter-basiert (pH, Temp, EC, Flow usw.)
- API: `GET/POST /api/v1/calibration`, `PATCH /api/v1/calibration/{id}`, `GET /api/v1/calibration/overview`

**Wartung (`MaintenanceRecord`)**
- Wartungstypen: `cleaning`, `inspection`, `replacement`, `tubing_flush`, `filter_change`, `pump_service`, `general_service`
- Status: `scheduled`, `done`, `overdue`, `skipped`
- API: `GET/POST /api/v1/maintenance`, `PATCH /api/v1/maintenance/{id}`, `GET /api/v1/maintenance/overview`

**Safety Incidents (`SafetyIncident`)**
- Incident-Typen: `calibration_expired`, `node_offline`, `dry_run_risk`, `clogging_suspected`, u.a.
- Schweregrade: `info`, `warning`, `high`, `critical`
- Status: `open`, `acknowledged`, `resolved`
- API: `GET/POST /api/v1/safety/incidents`, `PATCH /api/v1/safety/incidents/{id}`, `GET /api/v1/safety/overview`

**Command-Guard-Logik**
- Reactor-Commands werden serverseitig geprueft, bevor sie an MQTT weitergegeben werden
- Blockiergruende: kritischer offener Incident, offline/error Node fuer sicherheitssensitive Commands, `dry_run_risk`-Incident fuer Pumpe/Aeration, abgelaufene Kalibrierung fuer Sample-Capture
- Geblockte Commands erhalten `status=blocked` + `blocked_reason`
- Kein echtes Hardware-Interlock in diesem Schritt – nur Protokollierung und UI-Sichtbarkeit

**Dashboard-Integration**
- KPIs: offene Incidents, faellige/abgelaufene Kalibrierungen, ueberfaellige Wartung

**Frontend**
- Neue Seite `/safety` mit Tabs: Incidents, Kalibrierung, Wartung
- Dashboard zeigt Safety-KPIs mit Farbwarnungen
- Navigation-Link "Safety" in AppShell

### Was bewusst noch nicht enthalten ist

- echte Hardware-Abschaltung / GPIO-Safe-State
- ACK/Retry fuer Commands
- PID-Regelung / Scheduler
- automatische Kalibrierablaeuf
- MQTT-Haertung / TLS
- Compliance-/Audit-Framework
- vollautomatische Safety-Steuerung

### Grundlage fuer

- Command ACK / Retry
- Scheduler mit Guard-Bedingungen
- Vision Node
- echte Hardware-Kommandos mit Safety-Gate
- geschlossene Regelkreise

## Command ACK / Retry V1

Diese Schicht macht Zustellung und Bestaetigung von Reactor-Commands nachvollziehbar und erlaubt gezieltes Retry fehlgeschlagener Kommandos.

### Was enthalten ist

**ReactorCommand-Erweiterung**
- `command_uid` (UUID) als Korrelations-ID fuer MQTT/Node-Antwortkette
- `published_at`, `acknowledged_at`, `timeout_at` zur Status-Nachverfolgung
- `retry_count`, `max_retries` (Default 3)
- `last_error`, `ack_payload` (JSON des Node-Rueckmeldung)
- Erweiterte Status-Werte: `pending`, `sent`, `acknowledged`, `failed`, `blocked`, `timeout`, `retrying`

**MQTT-Topic-Erweiterung**
- Publish-Payload traegt jetzt `command_uid` mit
- Neues ACK-Topic `labos/reactor/{reactor_id}/ack` (JSON-Payload `{command_id, command_uid, status, error?, received_at?}`)
- Bridge abonniert den ACK-Stream und markiert Commands als `acknowledged` bzw. `failed`

**Retry + Timeout**
- `POST /api/v1/reactor-commands/{id}/retry` (Operator/Admin) inkrementiert `retry_count`, republiziert ueber die Bridge und startet das Timeout neu
- `POST /api/v1/reactor-commands/check-timeouts` setzt nicht bestaetigte `sent`/`retrying` Commands mit abgelaufenem `timeout_at` auf `timeout`
- Standard-ACK-Timeout: 30 s (`COMMAND_ACK_TIMEOUT_SECONDS`)

**Frontend**
- Command-Tabelle zeigt ACK-Zeitstempel, Retry-Zaehler und Fehlermeldungen
- Retry-Button fuer fehlgeschlagene/zeitueberschrittene Commands (Rollenfilter)

**Simulator / Beispiel-Node**
- `scripts/mqtt/simulate_env_node.py` abonniert Control-Topics und publiziert ACKs (optional mit `--ack-error-rate` fuer NACK-Tests)
- `examples/esp32/env_node_example.ino` extrahiert `command_id`/`command_uid` und sendet ACK zurueck

### Was bewusst noch nicht enthalten ist

- automatischer Retry-Scheduler / Background-Worker
- QoS 1/2, Retained-ACK-Semantik
- Kompletter Audit-Trail-Export
- Multi-Broker oder Broker-Failover

## Scheduler / Automation Runtime V1

Diese Schicht macht zeitbasierte Automation moeglich, ohne einen externen Scheduler (Celery, k8s CronJob usw.) einzufuehren.

### Was enthalten ist

**Schedule-Modell**
- `schedule_type`: `interval`, `cron` (5-Feld Minute/Stunde/Tag/Monat/Wochentag) oder `manual`
- `target_type`: `command` (Reactor-Command ueber den Safety-Guard-Pfad) oder `rule` (ruft die Rule-Evaluation)
- `target_params` (JSON) traegt z.B. `command_type` fuer Command-Schedules oder `dry_run` fuer Rule-Schedules
- Felder: `last_run_at`, `next_run_at`, `last_status`, `last_error`

**ScheduleExecution-Log**
- `status` (`success`|`failed`|`skipped`), `trigger` (`scheduler`|`manual`), Start/Finish, Ergebnis-JSON, Fehler
- Pro Schedule werden die juengsten 100 Ausfuehrungen aufbewahrt

**Runtime**
- `SchedulerRunner` laeuft als Daemon-Thread im FastAPI-Lifespan
- Tick alle `scheduler_tick_seconds` (Default 5 s)
- Faellige Schedules werden sequentiell ausgefuehrt, Fehler werden pro Schedule geloggt und brechen den Tick nicht ab
- `scheduler_enabled` und `scheduler_tick_seconds` sind ueber `.env` konfigurierbar

**API (Operator fuer Writes, Authenticated fuer Reads)**
- `GET/POST /api/v1/schedules`
- `PATCH /api/v1/schedules/{id}` und `PATCH /api/v1/schedules/{id}/enabled`
- `DELETE /api/v1/schedules/{id}`
- `GET /api/v1/schedules/{id}/executions`
- `POST /api/v1/schedules/{id}/run`

**Frontend**
- Neue Seite `/schedules` mit Formular, Uebersichtstabelle, Enable/Disable, Manuell ausfuehren und Ausfuehrungshistorie
- Navigation-Link "Scheduler" in AppShell

**Seed-Beispiele (initial deaktiviert)**
- Lichtzyklus Reaktor A1 (Interval 12 h, light_on)
- Regel-Check alle 60 s (Rule "Sensor ohne Werte 24h")
- Telemetrie-Sampling Trigger (Interval 5 min, sample_capture)
- Wartungscheck taeglich (Cron `0 7 * * *`, Rule dry-run)

### Was bewusst noch nicht enthalten ist

- verteilte Worker / Parallelausfuehrung
- vollstaendige Cron-Syntax (Nicknames, L/W/#, Sekunden)
- DAG-/Workflow-Orchestrierung
- Uebergeordneter Retry-Controller fuer fehlgeschlagene Schedule-Runs

## Struktur

```text
LabOS/
├── apps/frontend        # Next.js 14 Web UI
├── services/api         # FastAPI Backend
├── docs/wiki            # integriertes Markdown-Wiki
├── infra/docker         # optionale Infra-Dateien
├── configs              # Beispielkonfigurationen
└── scripts              # Hilfsskripte
```

## Schnellstart

```bash
cp .env.example .env
mkdir -p storage/wiki storage/photos

docker compose up --build
```

Danach:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MQTT Broker: `mqtt://localhost:1883`
- MQTT over WebSockets: `ws://localhost:9001`

Beim API-Start werden zuerst Alembic-Migrationen bis `head` ausgefuehrt. Danach ergänzt der Seed-Flow nur fehlende Demo-Daten fuer Charges, Assets, Inventory, Labels, Wiki, Sensoren, Tasks, Alerts und Regeln.

Fuer Auth / Rollen V1 sind zusaetzlich diese `.env`-Variablen relevant:

- `AUTH_SECRET_KEY`
- `AUTH_COOKIE_NAME`
- `AUTH_COOKIE_SECURE`
- `AUTH_TOKEN_TTL_HOURS`
- `BOOTSTRAP_ADMIN_USERNAME`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `BOOTSTRAP_ADMIN_DISPLAY_NAME`
- `BOOTSTRAP_ADMIN_EMAIL`
- `MQTT_ENABLED`
- `MQTT_BROKER_HOST`
- `MQTT_BROKER_PORT`
- `MQTT_CLIENT_ID`
- `MQTT_TOPIC_PREFIX`
- `MQTT_PUBLISH_COMMANDS`

Beim ersten Start bootstrapped LabOS genau einen lokalen Admin nur dann, wenn in `useraccount` noch kein Benutzer vorhanden ist.

## Rollen / Auth V1

LabOS bringt jetzt eine lokale Mehrnutzerbasis ohne externe Identity-Abhaengigkeit mit.

Enthalten:

- lokales `UserAccount`-Modell mit Passwort-Hash, Rolle, Aktivstatus und letztem Login
- Login ueber `POST /api/v1/auth/login`
- Session-Cookie plus API-Token fuer Browser und Skriptzugriffe
- `GET /api/v1/auth/me` fuer Session-Aufloesung im Frontend
- `POST /api/v1/auth/logout` zum lokalen Session-Clear
- Admin-verwaltete User-API unter `/api/v1/users`
- serverseitige Rollenpruefung auf kritischen Schreibpfaden

Rollen:

- `viewer`: Lesezugriff auf geschuetzte LabOS-Bereiche, keine kritischen Schreibaktionen
- `operator`: operative Schreibaktionen fuer Chargen, Reaktoren, Assets, Inventory, Labels, Fotos, Sensorwerte, Tasks und Alerts
- `admin`: volle Kontrolle inklusive Benutzerverwaltung, Regeln und systemnahen ABrain-/Admin-Pfaden

Geschuetzte API-Logik:

- nahezu alle `/api/v1/*`-Routen verlangen Anmeldung
- bewusst offen bleiben nur `/`, `/healthz` und `POST /api/v1/auth/login`
- Sensorwert-Ingest ist in V1 nicht anonym offen, sondern mindestens `operator`-geschuetzt
- Userverwaltung unter `/api/v1/users` ist ausschliesslich `admin`

Bewusst noch nicht enthalten:

- OAuth / OIDC / SSO
- LDAP
- Passwort-Reset per Mail
- 2FA
- Multi-Tenant- oder Teammodell
- feingranulare Objektberechtigungen
- serverseitige Token-Revocation-Liste

Bootstrap-Login fuer lokale Dev-Umgebungen:

```bash
curl -c .labos-cookie.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"labosadmin"}'
```

Session pruefen:

```bash
curl -b .labos-cookie.txt http://localhost:8000/api/v1/auth/me
```

Die folgenden API-Beispiele in dieser README setzen eine aktive Session voraus. Fuer `curl` sollte deshalb dieselbe Cookie-Datei mit `-b .labos-cookie.txt` weiterverwendet werden.

## ReactorOps / Digital Twin V1

ReactorOps erweitert LabOS von einfachem Reactor-CRUD hin zu gefuehrten biologischen und technischen Prozessobjekten.

Unterschied zu reinem Reactor-CRUD:

- `Reactor` bleibt der Stammdatensatz fuer Typ, Volumen, Standort und Grundstatus
- `ReactorTwin` bildet den laufenden Betriebszwilling mit Phase, biologischem Zustand, technischem Zustand und Zielbereichen
- `ReactorEvent` dokumentiert Inokulationen, Beobachtungen, Mediumwechsel, Wartung und Vorfaelle als kleine Prozesshistorie

Enthalten:

- pro Reaktor ein Reactor-Twin mit Phase, Sollbereichen und Kontextfeldern
- biologische Zustandsbasis: `stable`, `adapting`, `growing`, `stressed`, `contaminated`, `unknown`
- technische Zustandsbasis: `nominal`, `warning`, `maintenance`, `degraded`, `error`
- Prozessphasen: `inoculation`, `growth`, `stabilization`, `harvest_ready`, `maintenance`, `paused`, `incident`
- optionale Kontaminationskennzeichnung: `suspected`, `confirmed`, `recovering`, `cleared`
- Event-Historie fuer Eingriffe und Beobachtungen
- aggregierte Einbindung von Tasks, Alerts, Photos und Sensoren pro Reaktor
- ReactorOps-Seite unter `/reactor-ops` und kleine Dashboard-KPIs

Backend-Endpunkte:

- `GET /api/v1/reactor-ops`
- `GET /api/v1/reactor-ops/{reactor_id}`
- `POST /api/v1/reactor-ops`
- `PUT /api/v1/reactor-ops/{reactor_id}`
- `PATCH /api/v1/reactor-ops/{reactor_id}/phase`
- `PATCH /api/v1/reactor-ops/{reactor_id}/state`
- `GET /api/v1/reactors/{reactor_id}/events`
- `POST /api/v1/reactors/{reactor_id}/events`

Bewusst noch nicht enthalten:

- echte Hardware- oder Firmware-Ansteuerung
- Scheduler fuer Licht-/Temperaturzyklen
- Dosing-Logik
- PID-Regelung
- Kalibrier-Workflows als eigenes Modul
- Safety-/Interlock-Systeme
- Multi-Reactor-Orchestrierung
- komplexe Medien-/Rezept-Engine

ReactorOps V1 schafft damit die Bruecke zwischen Reactor-Stammdaten, Sensorik, Fotos, Alerts und spaeterer Reactor Control / Telemetry / Calibration / Safety.

## Reactor Control / Telemetry V1

Reactor Control erweitert LabOS von reinem Soll- und Prozesskontext auf die erste Ist-/Control-Schicht.

Unterschied zu ReactorOps:

- `ReactorOps` beschreibt den digitalen Betriebszwilling: Phase, biologischer Zustand, technischer Zustand und Zielkorridore
- `Reactor Control` sammelt reale Telemetrie, verwaltet Setpoints, fuehrt Devices/Nodes und protokolliert vorbereitete Kommandos
- in V1 bleibt die Hardwareausfuehrung bewusst aus; LabOS baut nur die saubere Bruecke zwischen Twin, Telemetrie und spaeterer Geraeteintegration

Enthalten:

- `TelemetryValue` als leichte Zeitreihen-Tabelle pro Reaktor fuer `temp`, `ph`, `light`, `flow`, `ec`, `co2` und `humidity`
- `DeviceNode` als minimale Hardware-/Node-Schicht fuer ESP32-, Sensor-Bridge- oder Controller-Knoten
- `ReactorSetpoint` fuer Zielwerte und optionale Min-/Max-Korridore pro Parameter
- `ReactorCommand` als Command-Log bzw. Stub-Queue ohne echte Ausfuehrung
- Reactor-Control-Seite unter `/reactor-control`
- Dashboard-Erweiterung mit letztem Telemetriezeitpunkt, Temp-/pH-Uebersicht und Offline-Devices

Backend-Endpunkte:

- `POST /api/v1/telemetry`
- `GET /api/v1/reactors/{reactor_id}/telemetry`
- `GET /api/v1/reactors/{reactor_id}/telemetry/latest`
- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `PATCH /api/v1/devices/{device_id}`
- `GET /api/v1/reactors/{reactor_id}/setpoints`
- `POST /api/v1/reactors/{reactor_id}/setpoints`
- `PATCH /api/v1/setpoints/{setpoint_id}`
- `POST /api/v1/reactors/{reactor_id}/commands`
- `GET /api/v1/reactors/{reactor_id}/commands`

Beispiel fuer Telemetry-Ingest:

```bash
curl -b .labos-cookie.txt -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{"reactor_id":1,"sensor_type":"temp","value":29.8,"unit":"degC","source":"device"}'
```

Setpoints pro Reaktor abrufen:

```bash
curl -b .labos-cookie.txt http://localhost:8000/api/v1/reactors/1/setpoints
```

Bewusst noch nicht enthalten:

- MQTT
- WebSockets
- GPIO- oder Firmware-Aufrufe
- PID-Regelung
- Scheduler fuer Licht-/Temperaturzyklen
- Dosing-Logik
- echte Command-Dispatch- oder ACK-Pipelines
- externe Device-Services

Reactor Control / Telemetry V1 schafft damit die erste belastbare Bruecke von ReactorOps-Sollzustand zu realen Ist-Werten und bereitet spaetere Hardwareintegration, Automation, Calibration und Safety sauber vor.

## MQTT / ESP32 / Pi Architektur V1

Mit MQTT V1 bekommt LabOS jetzt die erste echte lokale Messaging- und Node-Schicht zwischen API, Raspberry Pi und spaeteren ESP32-/Edge-Nodes.

Unterschied zur reinen Reactor-Control-REST-Schicht:

- `Reactor Control / Telemetry` definiert Datenmodelle und API fuer Telemetrie, Setpoints, Devices und Commands
- `MQTT V1` fuehrt den lokalen Bus ein, ueber den Nodes Telemetrie und Heartbeats senden und LabOS Commands publizieren kann
- die REST-Endpunkte bleiben erhalten und bilden weiterhin den stabilen Admin-/UI-Zugang

Enthalten:

- lokaler Mosquitto-Broker im Compose-Stack
- minimale Broker-Konfiguration unter `infra/mqtt/config/mosquitto.conf`
- Python-MQTT-Bridge im API-Service
- MQTT-Topic-Architektur fuer Telemetrie, Control und Node-Status
- MQTT -> `TelemetryValue` Persistierung
- MQTT -> `DeviceNode` Status-/Heartbeat-Update
- optionaler MQTT-Publish beim Erstellen eines `ReactorCommand`
- kleine MQTT-Statusanzeige in `/reactor-control`
- Referenzcode unter [examples/esp32/env_node_example.ino](/home/dev/LabOS/examples/esp32/env_node_example.ino:1)
- lokaler Simulator unter [scripts/mqtt/simulate_env_node.py](/home/dev/LabOS/scripts/mqtt/simulate_env_node.py:1)

Topic-Struktur V1:

- `labos/reactor/{reactor_id}/telemetry/{sensor_type}`
- `labos/reactor/{reactor_id}/control/{channel}`
- `labos/node/{node_id}/status`
- `labos/node/{node_id}/heartbeat`

Beispiel-Payloads:

Telemetry:

```json
{
  "value": 29.4,
  "unit": "degC",
  "source": "device",
  "node_id": "esp32-a1"
}
```

Node-Status:

```json
{
  "name": "ESP32 Env Node A1",
  "reactor_id": 1,
  "node_type": "env_control",
  "status": "online",
  "firmware_version": "v0.4.0"
}
```

Command-Publish aus LabOS:

- Topic: `labos/reactor/1/control/light`
- Payload:

```json
{
  "command_id": 11,
  "reactor_id": 1,
  "command_type": "light_on",
  "channel": "light",
  "command": "on",
  "source": "labos"
}
```

Lokaler Testpfad:

1. `docker compose up --build`
2. Login gegen LabOS durchfuehren
3. MQTT-Simulator starten:

```bash
cd /home/dev/LabOS
.venv/bin/python scripts/mqtt/simulate_env_node.py --host localhost --reactor-id 1 --node-id sim-env-a1
```

4. Reactor-Control-Seite unter `http://localhost:3000/reactor-control` beobachten

Bewusst noch nicht enthalten:

- MQTT-Auth, TLS oder WAN-Betrieb
- ACK / Retry
- WebSocket-Live-UI
- echte Hardwareausfuehrung oder GPIO-Zugriffe
- Scheduler
- PID-Regelung
- Auto-Discovery oder komplexe Device Registry
- Vision- oder Jetson-spezifische Node-Logik

Diese Schicht ist bewusst klein gehalten und bildet die lokale Grundlage fuer spaetere Calibration / Maintenance / Safety, ACK / Retry, Scheduler und weitere Edge-Nodes.

## CRUD-Stand fuer Chargen und Reaktoren

Die Weboberflaeche unter `/charges` und `/reactors` unterstuetzt jetzt:

- Listenansicht mit relevanten Kernfeldern
- Anlegen neuer Chargen und Reaktoren
- Bearbeiten bestehender Datensaetze
- direkten Statuswechsel aus der Liste
- sichtbare Loading- und Fehlerzustaende

Backend-Endpunkte:

- `GET /api/v1/charges`
- `GET /api/v1/charges/{id}`
- `POST /api/v1/charges`
- `PUT /api/v1/charges/{id}`
- `PATCH /api/v1/charges/{id}/status`
- `GET /api/v1/reactors`
- `GET /api/v1/reactors/{id}`
- `POST /api/v1/reactors`
- `PUT /api/v1/reactors/{id}`
- `PATCH /api/v1/reactors/{id}/status`

Kernfelder:

- Charge: `name`, `species`, `status`, `reactor_id`, `start_date`, `volume_l`, `notes`
- Reactor: `name`, `reactor_type`, `status`, `volume_l`, `location`, `last_cleaned_at`, `notes`

## Sensorik V1

LabOS verarbeitet jetzt erste Sensordaten direkt in PostgreSQL ohne zusaetzliche Time-Series-Datenbank.

Backend-Endpunkte:

- `GET /api/v1/sensors`
- `GET /api/v1/sensors/overview`
- `GET /api/v1/sensors/{id}`
- `POST /api/v1/sensors`
- `PUT /api/v1/sensors/{id}`
- `PATCH /api/v1/sensors/{id}/status`
- `POST /api/v1/sensors/{id}/values`
- `GET /api/v1/sensors/{id}/values`

Sensor-Felder:

- `name`
- `sensor_type`
- `unit`
- `status`
- `reactor_id`
- `location`
- `notes`
- `created_at`
- `updated_at`

SensorValue-Felder:

- `sensor_id`
- `value`
- `recorded_at`
- `source`

Unterstuetzte `sensor_type`-Werte:

- `temperature`
- `humidity`
- `water_temperature`
- `ph`
- `ec`
- `light`
- `co2`

Unterstuetzte `status`-Werte:

- `active`
- `inactive`
- `error`
- `maintenance`

Manueller Beispiel-Ingest:

```bash
curl -X POST http://localhost:8000/api/v1/sensors/1/values \
  -H "Content-Type: application/json" \
  -d '{"value": 23.7, "source": "manual"}'
```

Verlauf abrufen:

```bash
curl "http://localhost:8000/api/v1/sensors/1/values?limit=20"
```

## Tasks + Alerts V1

LabOS bildet jetzt auch operative Arbeitsschritte und Laborhinweise direkt im System ab.

Backend-Endpunkte fuer Tasks:

- `GET /api/v1/tasks`
- `GET /api/v1/tasks/{id}`
- `POST /api/v1/tasks`
- `PUT /api/v1/tasks/{id}`
- `PATCH /api/v1/tasks/{id}/status`

Backend-Endpunkte fuer Alerts:

- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{id}`
- `POST /api/v1/alerts`
- `PATCH /api/v1/alerts/{id}/ack`
- `PATCH /api/v1/alerts/{id}/resolve`

Task-Felder:

- `title`
- `description`
- `status`
- `priority`
- `due_at`
- `charge_id`
- `reactor_id`
- `asset_id`
- `created_at`
- `updated_at`
- `completed_at`

Task-Status:

- `open`
- `doing`
- `blocked`
- `done`

Task-Prioritaeten:

- `low`
- `normal`
- `high`
- `critical`

Alert-Felder:

- `title`
- `message`
- `severity`
- `status`
- `source_type`
- `source_id`
- `created_at`
- `acknowledged_at`
- `resolved_at`

Alert-Severity:

- `info`
- `warning`
- `high`
- `critical`

Alert-Status:

- `open`
- `acknowledged`
- `resolved`

UI-Flows:

- `/tasks` bietet Liste, Filter, Create/Edit und Statuswechsel
- `/alerts` zeigt offene und historische Alerts, erlaubt manuelles Anlegen sowie `ack` und `resolve`
- das Dashboard zeigt offene Tasks, heute faellige Tasks, kritische Alerts und die letzten Alerts

Manuelle API-Beispiele:

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Probe Charge X","status":"open","priority":"high","charge_id":1}'
```

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{"title":"Temperatur Warnung","message":"Medium ueber Soll","severity":"high","source_type":"sensor","source_id":1}'
```

```bash
curl -X PATCH http://localhost:8000/api/v1/alerts/1/ack
```

## Foto Upload + Vision Basis V1

LabOS kann jetzt Bilddokumentation lokal speichern, operativen Objekten zuordnen und als Grundlage fuer spaetere Vision-Auswertung bereitstellen.

Storage:

- Bilddateien werden lokal unter `storage/photos/YYYY/MM/` abgelegt
- die Datenbank speichert nur Metadaten und den relativen `storage_path`
- keine BLOB-Speicherung in PostgreSQL

Erlaubte Upload-Typen:

- `image/jpeg`
- `image/png`
- `image/webp`

Standard-Groessenlimit:

- `8 MiB` pro Upload

Backend-Endpunkte:

- `GET /api/v1/photos`
- `GET /api/v1/photos/{id}`
- `POST /api/v1/photos/upload`
- `PUT /api/v1/photos/{id}`
- `GET /api/v1/photos/{id}/file`
- `GET /api/v1/photos/{id}/analysis-status`

Optionale Filter fuer `GET /api/v1/photos`:

- `charge_id`
- `reactor_id`
- `asset_id`
- `latest`
- `limit`

Photo-Felder:

- `filename`
- `original_filename`
- `mime_type`
- `size_bytes`
- `storage_path`
- `title`
- `notes`
- `charge_id`
- `reactor_id`
- `asset_id`
- `created_at`
- `uploaded_by`
- `captured_at`

UI-Flows:

- `/photos` bietet Upload-Formular, Filter, Galerie und Detailansicht
- Metadaten koennen nach dem Upload ueber die Detailansicht gepflegt werden
- das Dashboard zeigt Gesamtzahl, Uploads der letzten sieben Tage und die letzten Bild-Uploads

Manueller Upload per API:

```bash
curl -X POST http://localhost:8000/api/v1/photos/upload \
  -F "file=@./example.png" \
  -F "title=Reaktor A1 Tagesbild" \
  -F "reactor_id=1" \
  -F "notes=Farbe und Schaumbild dokumentieren"
```

Foto-Datei abrufen:

```bash
curl http://localhost:8000/api/v1/photos/1/file --output photo-1.bin
```

Vision-Stub pruefen:

```bash
curl http://localhost:8000/api/v1/photos/1/analysis-status
```

## ABrain Integration V1

LabOS stellt jetzt einen ersten datenbasierten Assistenz-Layer bereit, der echte Systemdaten zusammenfasst und fuer feste Laborfragen nutzbar macht.

Kontextquellen:

- offene und ueberfaellige Tasks
- kritische und offene Alerts
- Sensor-Overview und auffaellige Sensorzustände
- aktive Charges
- Reaktoren mit Status und offenen Tasks
- letzte Fotos

Backend-Endpunkte:

- `GET /api/v1/abrain/status`
- `GET /api/v1/abrain/presets`
- `GET /api/v1/abrain/context`
- `POST /api/v1/abrain/query`

Presets:

- `daily_overview`
- `critical_issues`
- `overdue_tasks`
- `sensor_attention`
- `reactor_attention`
- `recent_activity`

Antwortformat:

- `summary`
- `highlights`
- `recommended_actions`
- `referenced_entities`
- `used_context_sections`
- `fallback_used`

Fallback-Verhalten:

- standardmaessig arbeitet LabOS im lokalen Stub-Modus mit echter LabOS-Datengrundlage
- wenn `ABRAIN_USE_STUB=false` gesetzt wird, versucht LabOS ein externes ABrain unter `ABRAIN_BASE_URL`
- ist dieses nicht erreichbar, faellt der Query-Endpunkt sauber auf die lokale Assistenzlogik zurueck

Optionale Konfiguration:

- `ABRAIN_BASE_URL`
- `ABRAIN_USE_STUB`
- `ABRAIN_TIMEOUT_SECONDS`

Manuelle Beispiele:

```bash
curl http://localhost:8000/api/v1/abrain/context
```

```bash
curl -X POST http://localhost:8000/api/v1/abrain/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Was sind die wichtigsten offenen Punkte heute?","preset":"daily_overview"}'
```

Die Weboberflaeche unter `/abrain` bietet dazu Presets, freie Fragen, sichtbare Kontextbereiche und eine nachvollziehbare Antwortdarstellung.

## Regelengine / Automation V1

LabOS kann jetzt einfache, kontrollierte Regeln gegen aktuelle Systemdaten evaluieren und daraus Tasks oder Alerts erzeugen.

Unterstuetzte Trigger:

- `sensor_threshold`
- `stale_sensor`
- `overdue_tasks`
- `reactor_status`

Unterstuetzte Conditions:

- `threshold_gt`
- `threshold_lt`
- `age_gt_hours`
- `count_gt`
- `status_is`

Unterstuetzte Actions:

- `create_alert`
- `create_task`

Backend-Endpunkte:

- `GET /api/v1/rules`
- `GET /api/v1/rules/{id}`
- `POST /api/v1/rules`
- `PUT /api/v1/rules/{id}`
- `PATCH /api/v1/rules/{id}/enabled`
- `POST /api/v1/rules/{id}/evaluate`
- `GET /api/v1/rules/{id}/executions`
- `GET /api/v1/rules/executions`
- `POST /api/v1/rules/evaluate-all`

Dry-Run:

- `dry_run=true` evaluiert die Regel gegen aktuelle Daten, fuehrt aber keine Action aus
- jede Dry-Run- oder Echt-Ausfuehrung wird als Execution-Log gespeichert

Execution-Status:

- `matched`
- `not_matched`
- `executed`
- `failed`

V1-Grenzen:

- keine Hardwareaktionen
- keine Notifications
- keine Multi-Step-Workflows
- keine versteckte Scheduler-Magie

Manuelle Beispiele:

```bash
curl -X POST http://localhost:8000/api/v1/rules \
  -H "Content-Type: application/json" \
  -d '{"name":"Temperatur hoch","trigger_type":"sensor_threshold","condition_type":"threshold_gt","condition_config":{"sensor_id":1,"threshold":23.5},"action_type":"create_alert","action_config":{"title_template":"{sensor_name} zu hoch","message_template":"Sensor {sensor_name} meldet {value} {unit}.","severity":"high","source_type":"sensor"}}'
```

```bash
curl -X POST "http://localhost:8000/api/v1/rules/1/evaluate?dry_run=true"
```

```bash
curl http://localhost:8000/api/v1/rules/1/executions
```

Die Weboberflaeche unter `/rules` bietet Regelliste, Bearbeitung, Enable-Toggle, Dry-Run, echte Ausfuehrung und die letzten Execution-Logs.

## AssetOps / DeviceOps V1

LabOS bildet jetzt reale Geraete und Assets als operative Objekte ab, ohne daraus bereits ein ERP-, Einkaufs- oder CMDB-System zu machen.

Dieses V1 umfasst:

- Asset-Modell mit `name`, `asset_type`, `category`, `status`, `location`, `zone`
- optionale Betriebs- und Wartungsfelder wie `serial_number`, `manufacturer`, `model`, `maintenance_notes`
- `last_maintenance_at` und `next_maintenance_at`
- optionale `wiki_ref`
- Verknuepfung von Tasks und Photos ueber `asset_id`
- eigene AssetOps-Seite unter `/assets`
- Dashboard-KPIs fuer aktive Assets, Wartungsfaelle, Fehlerstatus und naechste Wartungen

Backend-Endpunkte:

- `GET /api/v1/assets`
- `GET /api/v1/assets/overview`
- `GET /api/v1/assets/{id}`
- `POST /api/v1/assets`
- `PUT /api/v1/assets/{id}`
- `PATCH /api/v1/assets/{id}/status`

Optionale Filter fuer `GET /api/v1/assets`:

- `status`
- `category`
- `location`
- `zone`

Unterstuetzte `asset_type`-Werte:

- `printer_3d`
- `microscope`
- `soldering_station`
- `power_supply`
- `pump`
- `server`
- `gpu_node`
- `sbc`
- `network_device`
- `lab_device`
- `tool`

Unterstuetzte Asset-Status:

- `active`
- `maintenance`
- `error`
- `inactive`
- `retired`

Abgrenzung zu spaeteren Modulen:

- AssetOps / DeviceOps beschreibt langlebige Geraete und Assets
- Inventory / MaterialOps beschreibt Materialien, Verbrauch und Lagerorte als eigene operative Ebene
- QR / Label, ITOps-Healthchecks und automatische Monitoring-Anbindung sind bewusst noch nicht Teil dieses Schritts

Warum dieser Schritt wichtig ist:

- schafft eine gemeinsame Objektbasis fuer BioOps, MakerOps und ITOps
- bereitet Inventory, QR, Traceability und spaetere Infra-/ITOps-Flows sauber vor
- haelt die Verknuepfung mit Tasks, Photos und Wiki lokal und nachvollziehbar

Beispiel:

```bash
curl -X POST http://localhost:8000/api/v1/assets \
  -H "Content-Type: application/json" \
  -d '{"name":"Prusa MK4","asset_type":"printer_3d","category":"MakerOps","status":"active","location":"Werkbank 1","zone":"Maker Corner","next_maintenance_at":"2026-04-30T10:00:00"}'
```

```bash
curl "http://localhost:8000/api/v1/assets?status=maintenance&location=Rack"
```

```bash
curl -X PATCH http://localhost:8000/api/v1/assets/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"error"}'
```

## Inventory / MaterialOps V1

LabOS bildet jetzt auch Materialien, Verbrauchsgueter und einfache Lagerlogik des Labs ab. Der Fokus bleibt bewusst pragmatisch: sichtbar machen, was vorhanden ist, wo es liegt und was knapp wird.

Dieses V1 umfasst:

- Inventory-Modell mit `name`, `category`, `status`, `quantity`, `unit`, `location`
- optionalen Mindestbestand ueber `min_quantity`
- optionale Lagerfeinheiten ueber `zone`
- optionale Felder wie `supplier`, `sku`, `notes`, `wiki_ref`, `last_restocked_at`, `expiry_date`
- optionale Asset-Verknuepfung ueber `asset_id`
- automatische Ableitung von `low_stock` und `out_of_stock` aus `quantity` und `min_quantity`
- eigene Inventory-Seite unter `/inventory`
- Dashboard-KPIs fuer Gesamtbestand, knappe Positionen, leere Positionen und kritische Materialien

Backend-Endpunkte:

- `GET /api/v1/inventory`
- `GET /api/v1/inventory/overview`
- `GET /api/v1/inventory/{id}`
- `POST /api/v1/inventory`
- `PUT /api/v1/inventory/{id}`
- `PATCH /api/v1/inventory/{id}/status`

Optionale Filter fuer `GET /api/v1/inventory`:

- `status`
- `category`
- `location`
- `zone`
- `search`
- `low_stock=true`

Unterstuetzte Kategorien:

- `filament`
- `electronic_component`
- `cable`
- `screw`
- `tubing`
- `chemical`
- `nutrient`
- `cleaning_supply`
- `spare_part`
- `consumable`
- `storage_box_content`

Unterstuetzte Inventory-Status:

- `available`
- `low_stock`
- `out_of_stock`
- `reserved`
- `expired`
- `archived`

Abgrenzung:

- AssetOps / DeviceOps beschreibt langlebige Geraete und Infrastruktur
- Inventory / MaterialOps beschreibt Materialien, Verbrauchsgueter, Ersatzteile und Lagerorte
- Beschaffung, Einkaufslisten, Batch-/Lot-Tracking und QR-Scanning sind bewusst noch nicht Teil von V1

Warum dieser Schritt wichtig ist:

- bildet die reale Materialebene von BioOps, MakerOps, KnowledgeOps und Automation endlich mit ab
- schafft eine saubere Grundlage fuer QR, Traceability, spaetere Nachkauf- und Verbrauchslogik
- verknuepft Materialien bei Bedarf bereits mit Assets, ohne eine komplexe Warenwirtschaft einzufuehren

Beispiele:

```bash
curl -X POST http://localhost:8000/api/v1/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"PLA Filament schwarz","category":"filament","status":"available","quantity":0.75,"unit":"kg","min_quantity":1.0,"location":"Werkbank 1","zone":"Maker Corner","asset_id":1}'
```

```bash
curl "http://localhost:8000/api/v1/inventory?low_stock=true&location=Werkbank"
```

```bash
curl -X PATCH http://localhost:8000/api/v1/inventory/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"reserved"}'
```

## QR / Label / Traceability V1

LabOS verbindet jetzt reale Objekte direkt mit ihren digitalen Eintraegen. Assets und Inventory-Items koennen ueber Label-Codes und QR-Ziele eindeutig adressiert werden, ohne dass dafuer bereits Scanner-Hardware, Lagerbuchungen oder mobile Sonderlogik noetig sind.

Dieses V1 umfasst:

- separates `Label`-Modell mit `label_code`, `label_type`, `target_type`, `target_id`
- aktuell unterstuetzte Zielobjekte:
  - `asset`
  - `inventory_item`
- optionale `display_name`, `location_snapshot` und `note`
- Aktiv/Inaktiv-Status fuer Labels
- browserfaehige Zielseite unter `/scan/{labelCode}`
- QR-SVG-Ausgabe pro Label ueber die API
- eigene Label-/Traceability-Seite unter `/labels`
- Dashboard-KPIs fuer gelabelte Assets, gelabeltes Inventory und letzte Labels

Backend-Endpunkte:

- `GET /api/v1/labels`
- `GET /api/v1/labels/overview`
- `GET /api/v1/labels/{label_code}`
- `GET /api/v1/labels/{label_code}/target`
- `GET /api/v1/labels/{label_code}/qr`
- `POST /api/v1/labels`
- `PUT /api/v1/labels/{id}`
- `PATCH /api/v1/labels/{id}/active`

Unterstuetzte Label-Typen:

- `qr`
- `printed_label`

Wichtige Nutzung:

- QR auf Asset oder Material zeigt auf eine scanfaehige Browser-Seite
- Objektseiten in `/assets` und `/inventory` machen zugehoerige Labels sichtbar
- die Label-Verwaltung erlaubt Reaktivierung, Stilllegung und Re-Targeting einzelner Labels

Bewusst noch nicht enthalten:

- Barcode-Scanner-Integration
- mobile native App
- Inventur-Workflow
- Lagerbuchung
- Batch-/Lot-Tracking
- physische Etikettendrucker-Integration

Warum dieser Schritt wichtig ist:

- reale Objekte im Raum werden direkt mit LabOS verknuepfbar
- Boxen, Geraete und Materialien lassen sich schneller identifizieren
- spaetere Inventur-, Wartungs-, Verbrauchs- und Traceability-Flows bauen auf einer sauberen Referenzschicht auf

Beispiele:

```bash
curl -X POST http://localhost:8000/api/v1/labels \
  -H "Content-Type: application/json" \
  -d '{"target_type":"asset","target_id":1,"label_type":"qr","display_name":"Prusa MK4 QR"}'
```

```bash
curl http://localhost:8000/api/v1/labels/LBL-AST-PRUSA-MK4/target
```

```bash
curl http://localhost:8000/api/v1/labels/LBL-AST-PRUSA-MK4/qr
```

Hinweis fuer QR-Ziele:

- `PUBLIC_WEB_BASE_URL` steuert die Browser-Zieladresse fuer `/scan/{labelCode}`
- `PUBLIC_API_BASE_URL` steuert die ausgelieferten QR-/API-Links
- Standardwerte sind lokal `http://localhost:3000` und `http://localhost:8000`

## Migrationen

Alembic liegt unter `services/api/alembic`. Die Baseline-Migration ersetzt die bisherige implizite Schema-Reparaturlogik und bildet die aktuelle Core-Struktur reproduzierbar ab.

Lokales Upgrade:

```bash
DATABASE_URL=postgresql+psycopg://labos:labos@localhost:5432/labos .venv/bin/alembic -c services/api/alembic.ini upgrade head
```

Neue Migration erzeugen:

```bash
DATABASE_URL=postgresql+psycopg://labos:labos@localhost:5432/labos .venv/bin/alembic -c services/api/alembic.ini revision --autogenerate -m "describe schema change"
```

Docker-Workflow:

```bash
make migrate-api
make make-migration MSG="describe schema change"
```

Hinweis:

- im Docker-Compose-Setup zeigt `DATABASE_URL` auf den Service-Namen `db`
- fuer Host-Kommandos ausserhalb des Containers sollte `DATABASE_URL` auf `localhost:5432` gesetzt werden

Bei Schemaaenderungen gilt:

- zuerst SQLModel-Modelle anpassen
- dann Alembic-Revision mit `--autogenerate` erzeugen
- generierte Migration pruefen und nachhaerten
- danach Tests laufen lassen

## Tests

API-Tests lokal:

```bash
python3 -m venv .venv
.venv/bin/pip install -r services/api/requirements.txt
.venv/bin/pytest services/api/tests -q
```

Migrationen explizit pruefen:

```bash
.venv/bin/pytest services/api/tests/test_migrations.py -q
```

Nur Sensorik-API pruefen:

```bash
.venv/bin/pytest services/api/tests/test_sensors_api.py -q
```

Nur Tasks- und Alerts-API pruefen:

```bash
.venv/bin/pytest services/api/tests/test_tasks_api.py services/api/tests/test_alerts_api.py -q
```

Nur Foto-API pruefen:

```bash
.venv/bin/pytest services/api/tests/test_photos_api.py -q
```

Nur AssetOps pruefen:

```bash
.venv/bin/pytest services/api/tests/test_assets_api.py -q
```

Nur Inventory / MaterialOps pruefen:

```bash
.venv/bin/pytest services/api/tests/test_inventory_api.py -q
```

Nur QR / Label / Traceability pruefen:

```bash
.venv/bin/pytest services/api/tests/test_labels_api.py -q
```

Nur ABrain-API pruefen:

```bash
.venv/bin/pytest services/api/tests/test_abrain_api.py -q
```

Nur Regelengine-API pruefen:

```bash
.venv/bin/pytest services/api/tests/test_rules_api.py -q
```

Frontend-Build lokal:

```bash
cd apps/frontend
npm install --no-package-lock
npm run build
```

Persistenz-Hinweis:

- `storage/photos` sollte im lokalen oder Docker-Setup persistent gehalten werden
- die Datenbank referenziert nur Metadaten; manuell geloeschte Dateien fuehren zu fehlenden Dateiverweisen

## Noch offen

- Delete-/Archivierungsstrategie fuer Chargen und Reaktoren
- automatische Sensor-zu-Alert-Regeln
- Benachrichtigungskanaele fuer Alerts
- Verknuepfung von Tasks, Sensorik und Wiki mit den CRUD-Objekten
- Vision-Auswertung und Bildanalyse auf Basis der gespeicherten Fotos
- externe ABrain-Anbindung mit stabiler Produktionsschnittstelle
- kontrollierte Scheduler-Anbindung fuer Regelevaluationen
- Relationen und fachliche Constraints fuer weitere Module gezielt erweitern
- Automationslogik kontrolliert auf Sensordaten und Aufgaben aufbauen
- Inventur-, Verbrauchs- und Nachkauf-Flows auf Label- und Inventory-Daten aufbauen

## Nächste Schritte

1. Inventur- und Traceability-Workflows auf dem Label-Fundament aufsetzen
2. Regelengine kontrolliert um geplante Evaluationen und weitere sichere Trigger erweitern
3. Externe ABrain-Anbindung stabilisieren und spaeter kontrolliert erweitern
4. Vision-Analyse kontrolliert an gespeicherte Fotos anbinden
5. Delete-/Archivierungsstrategie sauber festziehen
