# LabOS

LabOS ist ein Raspberry-Pi-taugliches Labor-Betriebssystem für Planung, Protokollierung, Live-Monitoring, Wiki, Automatisierung und KI-Assistenz.

## V1 Scope

- Dashboard
- Chargenverwaltung mit Create/Edit/Statuswechsel
- Reaktorverwaltung mit Create/Edit/Statuswechsel
- Sensorik V1 mit CRUD, Werte-Ingest und Verlauf
- Task- und Alert-Basis
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

Beim API-Start werden jetzt zuerst Alembic-Migrationen bis `head` ausgefuehrt. Danach wird nur dann Seed-Datenmaterial eingespielt, wenn noch keine Charges vorhanden sind.

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

Frontend-Build lokal:

```bash
cd apps/frontend
npm install --no-package-lock
npm run build
```

## Noch offen

- Delete-/Archivierungsstrategie fuer Chargen und Reaktoren
- Verknuepfung von Tasks, Sensorik und Wiki mit den CRUD-Objekten
- Relationen und fachliche Constraints fuer weitere Module gezielt erweitern
- Alerts, Aufgaben und Automationslogik auf Sensordaten aufbauen

## Nächste Schritte

1. Alerts und Tasks auf Sensordaten aufsetzen
2. ABrain-Integration auf echte LabOS-Daten erweitern
3. Auth und Rollenmodell ergaenzen
4. Delete-/Archivierungsstrategie sauber festziehen
5. Automationsregeln kontrolliert anbinden
