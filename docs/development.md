# Development

## Backend

### Virtual Environment einrichten

```bash
python3 -m venv .venv
.venv/bin/pip install -r services/api/requirements.txt
```

### Tests ausführen

Komplette API-Testsuite:

```bash
.venv/bin/pytest services/api/tests -q
```

Gezielte Module:

```bash
.venv/bin/pytest services/api/tests/test_migrations.py -q
.venv/bin/pytest services/api/tests/test_sensors_api.py -q
.venv/bin/pytest services/api/tests/test_tasks_api.py services/api/tests/test_alerts_api.py -q
.venv/bin/pytest services/api/tests/test_photos_api.py -q
.venv/bin/pytest services/api/tests/test_assets_api.py -q
.venv/bin/pytest services/api/tests/test_inventory_api.py -q
.venv/bin/pytest services/api/tests/test_labels_api.py -q
.venv/bin/pytest services/api/tests/test_abrain_api.py -q
.venv/bin/pytest services/api/tests/test_rules_api.py -q
.venv/bin/pytest services/api/tests/test_approvals_api.py -q
.venv/bin/pytest services/api/tests/test_boundary_invariants.py -q
```

### API lokal starten

```bash
DATABASE_URL=postgresql+psycopg://labos:labos@localhost:5432/labos \
  .venv/bin/uvicorn app.main:app --app-dir services/api --reload
```

## Migrationen

Alembic liegt unter `services/api/alembic`. Die Baseline-Migration ersetzt die bisherige implizite Schema-Reparaturlogik.

Lokales Upgrade:

```bash
DATABASE_URL=postgresql+psycopg://labos:labos@localhost:5432/labos \
  .venv/bin/alembic -c services/api/alembic.ini upgrade head
```

Neue Migration erzeugen:

```bash
DATABASE_URL=postgresql+psycopg://labos:labos@localhost:5432/labos \
  .venv/bin/alembic -c services/api/alembic.ini revision --autogenerate -m "describe schema change"
```

Docker-Workflow:

```bash
make migrate-api
make make-migration MSG="describe schema change"
```

Hinweis:

- Im Docker-Compose-Setup zeigt `DATABASE_URL` auf den Service-Namen `db`.
- Für Host-Kommandos außerhalb des Containers sollte `DATABASE_URL` auf `localhost:5432` gesetzt werden.

Bei Schemaänderungen:

1. zuerst SQLModel-Modelle anpassen
2. dann Alembic-Revision mit `--autogenerate` erzeugen
3. generierte Migration prüfen und nachhärten
4. danach Tests laufen lassen

## Frontend

```bash
cd apps/frontend
npm install --no-package-lock
npm run dev    # Dev-Server
npm run build  # Produktionsbuild
```

Lade- und Fehlerzustände müssen sichtbar sein; mobile/touch-Tauglichkeit ist Pflicht (siehe [AGENTS.md](../AGENTS.md)).

## MQTT-Simulator

Für End-to-End-Tests mit MQTT ohne echte Hardware:

```bash
.venv/bin/python scripts/mqtt/simulate_env_node.py \
  --host localhost --reactor-id 1 --node-id sim-env-a1
```

Optional mit ACK-Fehlern zur Prüfung der Retry-Pipeline:

```bash
.venv/bin/python scripts/mqtt/simulate_env_node.py \
  --host localhost --reactor-id 1 --node-id sim-env-a1 --ack-error-rate 0.3
```

## Arbeitsweise

- Kleine thematisch saubere Commits.
- Schemas und Modelle konsistent halten.
- Für jede nicht-triviale Änderung: Code, Tests, Doku.
- Neue Fachmodule bekommen eine eigene Datei unter [`modules/`](modules/), kein Einbau in die Root-README.

Vollständige Arbeitsregeln: [AGENTS.md](../AGENTS.md).
