# LabOS

LabOS ist ein Raspberry-Pi-taugliches Labor-Betriebssystem für Planung, Protokollierung, Live-Monitoring, Wiki, Automatisierung und KI-Assistenz.

## V1 Scope

- Dashboard
- Chargenverwaltung mit Create/Edit/Statuswechsel
- Reaktorverwaltung mit Create/Edit/Statuswechsel
- Sensorik V1 mit CRUD, Werte-Ingest und Verlauf
- Tasks + Alerts V1 mit operativen Dashboards
- Foto Upload + Vision Basis V1
- ABrain Integration V1 mit echtem LabOS-Kontext
- Regelengine / Automation V1
- integriertes Wiki auf Markdown-Basis
- Docker-Compose-Setup für lokale Entwicklung

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

Beim API-Start werden zuerst Alembic-Migrationen bis `head` ausgefuehrt. Danach ergänzt der Seed-Flow nur fehlende Demo-Daten für Charges, Wiki, Sensoren, Tasks und Alerts.

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

## Nächste Schritte

1. Regelengine kontrolliert um geplante Evaluationen und weitere sichere Trigger erweitern
2. Externe ABrain-Anbindung stabilisieren und spaeter kontrolliert erweitern
3. Vision-Analyse kontrolliert an gespeicherte Fotos anbinden
4. Tasks enger mit Chargen, Reaktoren und Wiki verknuepfen
5. Delete-/Archivierungsstrategie sauber festziehen
