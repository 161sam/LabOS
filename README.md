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

### ROS + MQTT Hybrid Model

Both transports stay active side by side with a strict division of responsibility:

```text
Edge devices (ESP32, Arduino, …)          Robot runtime (ROS2 nodes)
              │                                       │
              ▼                                       ▼
           MQTT Broker                             rclpy
              │                                       │
              └────────────► LabOS API ◄──────────────┘
                          (Truth + Governance)
                                 │
                                 ▼
                     ABrain ◄─ MCP ◄─ Smolit-AI-Assistant
```

- **MQTT** — best-effort transport for low-power edge devices and simple telemetry.
- **ROS** — deterministic runtime for local robot workloads, high-frequency data and actions/services.
- **LabOS** — the single source of truth for state and governance.

Routing rules are enforced in code by `services/api/app/ros_mqtt_hybrid/`:

- Telemetry flows `MQTT → LabOS → ROS` and `ROS → LabOS → MQTT` (optional broadcast); the **loop guard** prevents a message that arrived on one transport from being echoed back to the same transport.
- Commands only originate from LabOS (`source='labos'`). Commands with `source='mqtt'` or `source='ros'` are rejected by the orchestrator — ROS callbacks that want to issue a command hand off through `abrain_execution.execute_action` first.
- Every cross-system message is wrapped in a `MessageEnvelope` (`message_id`, `source`, `ts`, `kind`, payload) and passes the `LoopGuard` so duplicates are dropped.
- `HybridTopicMapping` owns the canonical naming: MQTT `labos/reactor/{id}/telemetry/{sensor}` ↔ ROS `/labos/reactor/{id}/{sensor}`.

Example dispatch from LabOS-internal code (`reactor_control.create_reactor_command` already routes through this on command publish):

```python
from app.ros_mqtt_hybrid import (
    EnvelopeKind, MessageEnvelope, SourceTag, get_orchestrator,
)

get_orchestrator().publish_command(MessageEnvelope(
    source=SourceTag.labos,
    kind=EnvelopeKind.command,
    reactor_id=5,
    key='light_on',
))
```

### ROS Compatibility Layer

LabOS optionally exposes its reactor/device world to ROS2 through a thin compatibility layer in `services/api/app/ros/`: reactors appear as ROS nodes, telemetry mirrors to `/labos/reactor/{id}/{sensor_type}`, and commands are reachable as services at `/labos/reactor/{id}/{command_type}`. The layer is additive — MQTT stays in place — and acts as **transport only**. Inbound ROS service callbacks dispatch through `abrain_execution.execute_action` (Safety Guards, Role Checks, Approval Gate and Trace Layer all apply); ROS is never authorized to execute commands directly. `rclpy` is an optional runtime dependency; when absent the bridge stays dormant and reports its status. Settings: `ROS_ENABLED=false` (default), `ROS_NODE_NAME=labos`, `ROS_NAMESPACE=/labos`.

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

### ABrain V2 Integration Surface

The `/abrain` page in LabOS is the **Decision Surface** for the ABrain V2 LabOS reasoning use cases. LabOS itself does not reason — it calls ABrain and renders the result alongside LabOS-local governance (Approval, Execution, Trace).

Supported reasoning modes (delegated to ABrain V2 / MCP `abrain.reason_labos_<mode>`):

- `reactor_daily_overview`
- `incident_review`
- `maintenance_suggestions`
- `schedule_runtime_review`
- `cross_domain_overview`

The request/response contract is exposed at `POST /api/v1/abrain/adapter/reason`. The shape V2 fields (`summary`, `highlights`, `prioritized_entities`, `recommended_actions`, `recommended_checks`, `approval_required_actions`, `blocked_or_deferred_actions`, `used_context_sections`, `reasoning_mode`, `trace_id`) are rendered as structured panels instead of raw JSON. Recommendations link directly to `/approvals`, `/executions` and `/traces`, and the "Ausfuehren" / "Approval anfragen" buttons re-use the existing `/api/v1/abrain/execute` pipeline — Safety Guards, Role Checks, Approval Gate and Trace Layer all still apply. If the external ABrain is unreachable, LabOS falls back to the existing local adapter heuristic mapped into the same V2 shape (marked with `fallback_used=true`).

Quick-entry links: Safety → `incident_review`, ReactorOps → `reactor_daily_overview`, Schedules → `schedule_runtime_review`. The legacy ABrain Assistant and Adapter Console remain available collapsed below the Decision Surface.

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
