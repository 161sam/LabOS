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

## Tests

API-Tests lokal:

```bash
python3 -m venv .venv
.venv/bin/pip install -r services/api/requirements.txt
.venv/bin/pytest services/api/tests -q
```

Frontend-Build lokal:

```bash
cd apps/frontend
npm install --no-package-lock
npm run build
```

## Noch offen

- Delete-/Archivierungsstrategie fuer Chargen und Reaktoren
- Alembic-Migrationen fuer reproduzierbare Schemaaenderungen
- Verknuepfung von Tasks, Sensorik und Wiki mit den CRUD-Objekten

## Nächste Schritte

1. Alembic-Migrationen einfuehren
2. Sensoren und Sensorwerte anbinden
3. Tasks und Alerts enger an Chargen/Reaktoren koppeln
4. ABrain-Integration auf echte LabOS-Daten erweitern
5. Auth und Rollenmodell ergaenzen
