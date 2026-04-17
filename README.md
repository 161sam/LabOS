# LabOS

LabOS ist ein Raspberry-Pi-taugliches Labor-Betriebssystem für Planung, Protokollierung, Live-Monitoring, Wiki, Automatisierung und KI-Assistenz.

## V1 Scope

- Dashboard
- Chargenverwaltung mit Create/Edit/Statuswechsel
- Reaktorverwaltung mit Create/Edit/Statuswechsel
- Sensor-API
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

## Nächste Schritte

1. Sensoren und Sensorwerte anbinden
2. Tasks und Alerts enger an Chargen/Reaktoren koppeln
3. ABrain-Integration auf echte LabOS-Daten erweitern
4. Auth und Rollenmodell ergaenzen
5. Delete-/Archivierungsstrategie sauber festziehen
