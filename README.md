# LabOS

**Ein lokales, Pi-taugliches Operating System für Labore.**
LabOS verbindet BioOps, ReactorOps, MakerOps, ITOps, KnowledgeOps und Automation in einem modularen Monolithen — lokal betreibbar, ohne Cloud-Zwang.

<!--
Badge-Platzhalter — sobald CI, Releases und Lizenz final sind, hier reale Badges einsetzen.
Typische Badges: build, license, python, node, pre-commit, docker.
-->

![status](https://img.shields.io/badge/status-active%20development-blue)
![stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Postgres-0a7cff)
![platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204%2F5%20%7C%20x86__64-brightgreen)
![license](https://img.shields.io/badge/license-TBD-lightgrey)

---

## Why LabOS?

Echte Labore laufen nicht auf Dashboards, sondern auf Alltag: Reaktoren kalibrieren, Chargen dokumentieren, Sensoren pflegen, Geräte warten, Wissen weitergeben. LabOS macht diesen Alltag als **strukturiertes, lokales Betriebssystem** adressierbar — ohne ein eigenes Brain zu werden.

LabOS sitzt in einer klaren Architektur aus drei Rollen:

```text
Smolit-AI-Assistant  →  ABrain  →  LabOS (MCP / Tool Adapter)  →  LabOS API / DB
```

- **LabOS** liefert Domain-, Realitäts- und Tool-/State-System.
- **ABrain** übernimmt Brain, Governance, Planung.
- **Smolit-AI-Assistant** ist die Chat-/User-Ebene.

Details: [docs/architecture.md](docs/architecture.md).

## Screenshots

<!-- TODO: echte Screenshots einfügen, sobald UI-Stände finalisiert sind -->

| Dashboard | ReactorOps |
| --- | --- |
| _(Screenshot folgt — `apps/frontend/app/page.tsx`)_ | _(Screenshot folgt — `/reactor-ops`)_ |

| Safety | Scheduler |
| --- | --- |
| _(Screenshot folgt — `/safety`)_ | _(Screenshot folgt — `/schedules`)_ |

| Photos & Vision | Approvals |
| --- | --- |
| _(Screenshot folgt — `/photos`)_ | _(Screenshot folgt — `/approvals`)_ |

## Features

### Domain Core

- Chargen, Reaktoren, Sensorik, Tasks, Alerts, Fotos, Wiki
- AssetOps / DeviceOps, Inventory / MaterialOps, QR / Label / Traceability
- Rollen & Auth mit lokalen Benutzerkonten

### ReactorOps Stack

- ReactorOps / Digital Twin + Reactor Control / Telemetry
- MQTT / ESP32 / Pi-Architektur (Broker, Topic-Schema, Bridge)
- Command ACK / Retry (UID, ACK-Topic, Timeout)
- Calibration / Maintenance / Safety mit Command-Guards
- Scheduler (interval / cron / manual)
- Vision Node (Pillow-basierte Auto-Analyse)
- Sensor + Vision Fusion → Reactor Health

### AI Boundary Layer

- Boundary Hardening — Signal- statt Entscheidungs-Prinzip, harte LabOS/ABrain-Trennung
- ABrain Adapter (Phase 1–3) — Context Builder, Action Catalog, statisches `ACTION_MAP`, Execution-Log
- Approval System (HITL-Queue, Operator-UI, Re-Apply aller Safety-Guards)

Fachliche Tiefe pro Modul: [docs/modules/](docs/modules/).

## Status

LabOS befindet sich in **aktiver Entwicklung (Pre-1.0)**. Die bisher fertigen Module sind in [docs/overview.md](docs/overview.md) und [ROADMAP.md](ROADMAP.md) dokumentiert.

- Öffentliche APIs können sich ändern.
- Breaking Changes werden über Alembic-Migrationen und Release Notes kommuniziert.
- Backend-Testsuite: 188 Tests grün (Stand 2026-04-19).

## Getting Started

```bash
cp .env.example .env
mkdir -p storage/wiki storage/photos
docker compose up --build
```

- Frontend: <http://localhost:3000>
- API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>
- MQTT: `mqtt://localhost:1883` · WebSockets `ws://localhost:9001`

Vollständige Setup-Anleitung mit Bootstrap-Login und `.env`-Variablen: [docs/getting-started.md](docs/getting-started.md).

## Architecture

LabOS ist ein modularer Monolith aus:

- **FastAPI + SQLModel** Backend (`services/api`)
- **Next.js 14** Frontend (`apps/frontend`)
- **PostgreSQL** als primäre Datenhaltung, lokales Filesystem für Uploads
- **Mosquitto** MQTT-Broker (`infra/mqtt`) für Telemetrie-/Control-/ACK-Topics

Die Architecture Boundary zwischen LabOS (Domain/State/Execution) und ABrain (Planning/Governance) ist als Code-Invariante implementiert und testgeprüft. Siehe [docs/architecture.md](docs/architecture.md).

### MCP Server

LabOS exposes a JSON-RPC 2.0 Model Context Protocol server at `POST /api/v1/mcp` — the only official tool surface for ABrain. Tools come from the static `abrain_actions` catalog, execution is routed through `abrain_execution.execute_action` (so Safety Guards, Role Checks, Approval Gate and Trace Layer all still apply), and resources expose the `abrain_context` snapshot read-only.

Methods: `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`. Debug helpers: `GET /api/v1/mcp/tools`, `GET /api/v1/mcp/resources`. Settings: `MCP_ENABLED=true`, `MCP_DEBUG=false`.

Example:

```bash
curl -sS -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -b cookies.txt \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"labos.create_task","arguments":{"title":"via MCP"},"trace_id":"demo-1"}}'
```

## Documentation

Die gesamte Projekt-Dokumentation liegt unter [`docs/`](docs/):

- [Overview](docs/overview.md) — Produktbild, V1-Scope, Leitprinzipien
- [Architecture](docs/architecture.md) — Zielarchitektur, Boundary, Komponenten
- [Getting Started](docs/getting-started.md) — lokales Setup
- [Development](docs/development.md) — Tests, Migrationen, Frontend-Build
- [Contributing](docs/contributing.md) — Workflow, Commit-Stil, Qualitätskriterien
- [Modules](docs/modules/) — tiefe Fachmodul-Dokumentation

Die Runtime-Wiki-Inhalte (SOPs, How-tos) liegen unter [`docs/wiki/`](docs/wiki/).

## Contributing

Beiträge sind willkommen. Bitte vorher [docs/contributing.md](docs/contributing.md) und [AGENTS.md](AGENTS.md) (Arbeitsregeln, Architekturinvarianten) lesen.

Kurz:

- Kleine thematische Commits, Code + Tests + Doku gehören zusammen.
- Neue Fachmodule werden unter [`docs/modules/`](docs/modules/) dokumentiert — nicht in die Root-README.
- Architekturinvarianten (LabOS ≠ Brain, Safety ist einzige Blocker-Autorität, statisches `ACTION_MAP`) respektieren.

## License

Lizenz noch offen (`TBD`). Vorschläge und Diskussion willkommen.
