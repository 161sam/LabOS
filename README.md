# LabOS

LabOS ist ein Raspberry-Pi-taugliches Labor-Betriebssystem für Planung, Protokollierung, Live-Monitoring, Wiki, Automatisierung und KI-Assistenz.

## V1 Scope

- Dashboard
- Chargenverwaltung mit Create/Edit/Statuswechsel
- Reaktorverwaltung mit Create/Edit/Statuswechsel
- Sensorik V1 mit CRUD, Werte-Ingest und Verlauf
- Tasks + Alerts V1 mit operativen Dashboards
- integriertes Wiki auf Markdown-Basis
- ABrain-Connector als Platzhalter
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

Frontend-Build lokal:

```bash
cd apps/frontend
npm install --no-package-lock
npm run build
```

## Noch offen

- Delete-/Archivierungsstrategie fuer Chargen und Reaktoren
- automatische Sensor-zu-Alert-Regeln
- Benachrichtigungskanaele fuer Alerts
- Verknuepfung von Tasks, Sensorik und Wiki mit den CRUD-Objekten
- Relationen und fachliche Constraints fuer weitere Module gezielt erweitern
- Automationslogik kontrolliert auf Sensordaten und Aufgaben aufbauen

## Nächste Schritte

1. Sensorbasierte Alert-Regeln und einfache Eskalationen einziehen
2. Tasks enger mit Chargen, Reaktoren und Wiki verknuepfen
3. ABrain-Integration auf echte LabOS-Daten erweitern
4. Delete-/Archivierungsstrategie sauber festziehen
5. Automationsregeln kontrolliert anbinden
