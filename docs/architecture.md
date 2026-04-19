# Architecture

## Zielarchitektur

LabOS ist im Zielbild **nicht** selbst das Brain. Der geplante Aufbau ist:

```text
Smolit-AI-Assistant  →  ABrain  →  LabOS MCP Server / Tool Adapter  →  LabOS API / DB
```

### Rollenverteilung

- **LabOS** — Domain-, Realitäts- und Tool-/State-System.
  - ReactorOps, Telemetrie, Commands, Safety, Assets, Inventory, Vision, Scheduler
  - Operator-UI für den Menschen am Lab
  - lokale fachliche Guards: Kalibrierung, Safety-Incidents, Command-Guard
- **ABrain** — Brain, Governance, Planning, Execution Control, Trace, Audit, agentische Orchestrierung.
- **Smolit-AI-Assistant** — User-Interaktion, Sprache, UX, Chat mit dem Menschen.

### Entscheidungsregel

- LabOS beschreibt und kontrolliert die Laborrealität.
- ABrain entscheidet, plant und regiert die Ausführung.
- Der Smolit-AI-Assistant spricht mit dem Menschen.

### Konsequenz für die LabOS-Roadmap

- Der bestehende `/api/v1/abrain/*`-Stub ist eine **Übergangs-/Bridge-/Dev-Fallback-Schicht**, nicht der Endzustand.
- LabOS baut **kein** eigenes Planungs- oder Agenten-System und dupliziert **keine** ABrain-Governance.
- LabOS konzentriert sich auf Domain-Modell, klare Aktionen/Tools und die Adapter-Schicht nach ABrain.

## Architecture Boundary (Boundary Hardening V1)

Die Trennlinie zwischen LabOS und ABrain ist eine **harte Invariante** und wird im Code und in der Doku konsequent durchgehalten.

**LabOS ist:**

- Domain-System: Reaktoren, Chargen, Sensoren, Assets, Inventar, Vision-Rohdaten
- State-System: Telemetrie, Zustände, Commands, Schedules, Incidents, Kalibrierungen
- Execution-System: validiert und führt ABrain-Aktionen aus, sendet MQTT-Commands
- Signal-System: emittiert strukturierte Signale (`telemetry_out_of_range`, `vision_contamination_suspected`, `safety_incident_open`) als Kontext für ABrain

**LabOS ist nicht:**

- Decision-System: keine finalen Entscheidungen
- Planning-System: keine Multi-Step-Planung
- Governance-System: keine Approval-/Policy-Logik
- Orchestration-System: keine übergreifende Prozesssteuerung

### Invariante Code-Regeln

Dokumentiert als Modul-Docstrings im Backend:

- `services/rules.py` — **Local Automation / Fallback**. Jede `RuleExecution` trägt `action_result.execution_origin = 'labos_local'`.
- `services/scheduler.py` — **Execution Only**. Triggert konfigurierte Targets, keine if/else-Logik über Live-State.
- `services/reactor_health.py` — **Classification + Signal Emission**. Status ist Label, kein Entscheid.
- `services/vision.py` — **Feature Extraction + Classification only**. Keine automatischen Aktionen.
- `services/safety.py` — **Guard / Constraint**. Einzige Stelle, die Commands blockieren darf. `blocked_reason`-Strings beginnen mit `safety_guard:`.
- `services/reactor_control.py` — validiert → fragt Safety-Guard → führt aus.
- `services/mqtt_bridge.py` — **Transport Only**. Keine Logik.
- `services/abrain.py` — **Dev Fallback**, nicht das echte Brain. `mode='stub'` im Response sichtbar.
- `services/signals.py` — einheitlicher `emit_signal(signal_type, payload)`-Helper.

Invariant-Tests (`tests/test_boundary_invariants.py`) stellen sicher, dass Vision keine Tasks/Commands erzeugt, Reactor-Health keine Commands auslöst, und Safety die einzige Blocker-Autorität ist.

## Komponenten

```text
LabOS/
├── apps/frontend        # Next.js 14 Web UI
├── services/api         # FastAPI Backend (modularer Monolith)
├── infra/mqtt           # Mosquitto-Konfiguration
├── docs/                # Projekt-Dokumentation (diese Doku)
├── docs/wiki            # integriertes Markdown-Wiki (Runtime)
├── configs              # Beispielkonfigurationen
├── scripts              # Hilfsskripte (inkl. MQTT-Simulator)
├── examples             # ESP32-Beispielcode
└── storage              # lokale Laufzeitdaten (Fotos, Wiki-Uploads)
```

### Backend (`services/api`)

- FastAPI + SQLModel + Alembic
- Router unter `app/routers/` (dünn)
- Business-Logik in `app/services/`
- Schemas in `app/schemas.py`, Modelle in `app/models.py`
- Tests in `services/api/tests/`

### Frontend (`apps/frontend`)

- Next.js 14 (App Router) + TypeScript
- Routes unter `app/`, Komponenten in `components/`, API-Zugriff in `lib/`
- Auth / Rollen-Handling über `AuthProvider`

### Persistenzebene

- PostgreSQL (primäre Datenhaltung, alle Domänen-Entities)
- lokales Filesystem (`storage/photos`, `storage/wiki`) für Uploads
- Alembic-Migrationen sind Source of Truth für Schemaänderungen

### MQTT-/Node-Ebene

- Mosquitto als lokaler Broker
- Topic-Schema: `labos/reactor/{reactor_id}/telemetry/{sensor_type}`, `labos/reactor/{reactor_id}/control/{channel}`, `labos/node/{node_id}/status|heartbeat`, `labos/reactor/{reactor_id}/ack`
- MQTT-Bridge in `services/api/app/services/mqtt_bridge.py`

## ABrain-Adapter (aktueller Stand)

Die `/api/v1/abrain/*`-Schicht ist seit **Adapter Alignment V1 Phase 2** eine Thin-Adapter-Facade: Status und Query delegieren an `abrain_adapter`; Phase 3 hat Execution + Governance Flow ergänzt (statisches `ACTION_MAP`, `ABrainExecutionLog`, `POST /abrain/execute`). Approval System V1 baut darauf auf und gibt approval-pflichtigen Actions eine HITL-Queue (`/approvals`).

Details: [modules/abrain-adapter.md](modules/abrain-adapter.md), [modules/approvals.md](modules/approvals.md).
