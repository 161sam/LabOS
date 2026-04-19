# LabOS Documentation

Diese Doku ist der Einstiegspunkt für tiefergehende Informationen zu LabOS. Die Root-[README](../README.md) bleibt bewusst knapp und verweist hierher.

## Einstieg

- [Overview](overview.md) — Was LabOS ist, Produktbild, V1-Scope
- [Architecture](architecture.md) — Zielarchitektur, LabOS-Grenze, Module
- [Getting Started](getting-started.md) — Lokales Setup mit Docker Compose
- [Development](development.md) — Tests, Migrationen, Frontend-Build
- [Contributing](contributing.md) — Beiträge, Arbeitsweise, Commit-Stil

## Module

Die einzelnen Fachmodule sind unter [`modules/`](modules/) dokumentiert:

- [Reactor Stack](modules/reactor-ops.md) — ReactorOps / Digital Twin, Reactor Control, Telemetrie, MQTT, Command ACK/Retry
- [Safety, Calibration, Maintenance](modules/safety.md) — Command-Guards, Kalibrierung, Wartung, Incidents
- [Scheduler](modules/scheduler.md) — Interval/Cron/Manual-Schedules, Execution-Log
- [Reactor Health](modules/reactor-health.md) — Deterministische Fusion aus Telemetrie, Vision, Safety
- [Vision & Photos](modules/vision.md) — Foto-Upload, Vision-Analyse
- [ABrain Adapter](modules/abrain-adapter.md) — Boundary Hardening, Context Builder, Action Catalog, Execution Pipeline
- [Approval System](modules/approvals.md) — HITL-Queue für approval-pflichtige Actions
- [Operational Core](modules/operational-core.md) — Charges, Reactors, Sensors, Tasks, Alerts, Rules
- [Assets, Inventory, Labels](modules/assets-inventory.md) — AssetOps, MaterialOps, QR/Label/Traceability
- [Auth & Roles](modules/auth.md) — Lokale Benutzer, Rollen, Session

## Weitere Referenzen

- [ROADMAP.md](../ROADMAP.md) — Produkt- und Feature-Roadmap
- [AGENTS.md](../AGENTS.md) — Arbeitsregeln für Codex-/Agent-Workflows
- [`docs/wiki/`](wiki/) — Integriertes Projekt-Wiki (SOPs, How-tos, Betriebshinweise)
