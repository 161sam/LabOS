# ABrain Adapter

> Zielbild (siehe [architecture.md](../architecture.md)):
> `Smolit-AI-Assistant → ABrain → LabOS MCP / Tool Adapter → LabOS API / DB`.
> LabOS liefert Domain-State, Aktionen und Guards; ABrain liefert Planung, Governance und Reasoning. Der bestehende lokale `/api/v1/abrain/*`-Stub bleibt Übergangsschicht.

## Phasen-Überblick

- **Phase 1** — Context Builder, Action Catalog, Thin HTTP Client, Orchestrator, Console-UI
- **Phase 2** — Legacy `/abrain/status|query` als Thin Adapter (keine eigene Reasoning-/Fallback-Logik in `services/abrain.py`)
- **Phase 3** — Execution + Governance Flow (statisches `ACTION_MAP`, `ABrainExecutionLog`, `POST /abrain/execute`)

## Phase 1 — Adapter-Grundlagen

- **Context Builder** (`app/services/abrain_context.py`): deterministischer LabOS-Kontext mit Reactor-, Operations-, Resource- und Schedule-Sicht inkl. Reactor-Health-/Telemetrie-Bezug.
- **Action Catalog V1** (`app/services/abrain_actions.py`): 9 kuratierte Aktionen (`labos.create_task`, `labos.create_alert`, `labos.run_reactor_health_assessment`, `labos.create_reactor_command`, `labos.retry_reactor_command`, `labos.ack_safety_incident`, `labos.create_maintenance_record`, `labos.create_calibration_record`, `labos.run_schedule_now`) mit Risk-Level, Approval-Flag, Allowed-Roles, Guards.
- **Thin Client & Orchestrator** (`app/services/abrain_client.py`, `app/services/abrain_adapter.py`): HTTP-Aufruf an externes ABrain mit Timeout/Enable/Mode; deterministischer lokaler Fallback (`policy_decision=local_rules_v1`); Governance-Boundary gegen den statischen Katalog; Trace-ID.
- **Router-Endpoints:** `/api/v1/abrain/actions`, `/api/v1/abrain/adapter/context`, `/api/v1/abrain/adapter/query` (admin-only).
- **Frontend:** `ABrainAdapterConsole` auf `/abrain` mit Modus, Kontext-KPIs, Action-Katalog und Empfehlungen inkl. `risk_level`, `requires_approval`, `blocked`/`blocked_reason`, `trace_id`.
- **Config:** `ABRAIN_ENABLED`, `ABRAIN_MODE`, `ABRAIN_USE_LOCAL_FALLBACK`, `ABRAIN_ADAPTER_CONTRACT_VERSION` zusätzlich zu `ABRAIN_BASE_URL`, `ABRAIN_TIMEOUT_SECONDS`, `ABRAIN_USE_STUB`.

## Phase 2 — Thin Adapter Routing der Legacy-Schicht

- `services/abrain.py` ist reine Legacy-Facade ohne eigene Reasoning-/Fallback-Logik. `get_status()` und `query()` delegieren an `abrain_adapter` und projizieren die Adapter-Antwort in das Legacy-Schema `ABrainQueryResponse`.
- Fallback-Semantik bleibt erhalten: Wenn `ABRAIN_USE_STUB=true` oder das externe ABrain nicht erreichbar ist, liefert der Adapter eine lokale Antwort, die die Legacy-Route als `mode='stub'` zurückgibt.
- Einziger HTTP-Pfad nach ABrain: `abrain_client.py`. Neue Reasoning-Features gehen in den Adapter oder ins externe ABrain, nie zurück in `abrain.py`.
- Test `test_legacy_query_delegates_through_adapter` prüft den Adapter-Pfad der Legacy-Route.

## Phase 3 — Execution + Governance Flow

- `services/abrain_execution.py` mit **statischem `ACTION_MAP`** (`labos.create_task`, `labos.create_alert`, `labos.create_reactor_command`, `labos.retry_reactor_command`, `labos.ack_safety_incident`). Kein Eval/Reflection, kein Dynamic Registry — neue Actions erfordern Code-Review.
- Execution-Pipeline: Catalog-Lookup → Role-Check gegen `descriptor.allowed_roles` → Approval-Gate (`requires_approval` ohne `approve=True` → `pending_approval`, **keine Ausführung**) → Dispatch an bestehende Service-Layer-Funktionen → Result-Klassifikation → `ABrainExecutionLog`.
- Safety bleibt einzige Blocker-Autorität: Reactor-Commands laufen durch `reactor_control.create_reactor_command`, das lokal `safety_service.check_command_guards` ruft. Ein geblockter Command wird als `ABrainExecutionStatus.blocked` mit `blocked_reason='safety_guard: …'` protokolliert.
- Modell `ABrainExecutionLog` (Migration `20260419_0018`): `action`, `params`, `status`, `blocked_reason`, `executed_by`, `source`, `trace_id`, `result`, `created_at` mit Indizes auf `action`, `status`, `trace_id`, `created_at`.
- Endpoint `POST /api/v1/abrain/execute` (authenticated; Role-Enforcement im Service über den Katalog, nicht am Router). Rückgabe: `ABrainExecutionResult` mit `trace_id`-Propagation.
- Status-Enum `ABrainExecutionStatus`: `executed`, `pending_approval`, `blocked`, `rejected`, `failed`.

Approval-Gate + Queue + UI sind in [approvals.md](approvals.md) beschrieben.

## Bewusst außerhalb dieser Phasen

- vollwertiger MCP-Server (aktuell nur HTTP-Adapter-Endpunkte)
- externe Execution-Control / Approval-Pfad **durch ABrain selbst** (LabOS gated aktuell über `approve`-Flag im Request bzw. Approval-Queue; der Workflow drumherum gehört in ABrain bzw. Smolit)
- Rückkopplung externer Actions über den Adapter auf LabOS-Commands und -Events
- UI-Surface für `ABrainExecutionLog` (Historie, Filter nach `trace_id`/`status`)

## Governance-Regel

Reasoning-, Fallback- und Policy-Entscheidungen bleiben im Adapter. `abrain_execution` ist reiner Enforcement- und Audit-Pfad — kein Planning, kein Dynamic Routing. Neue Actions werden nur nach Review in `ACTION_MAP` aufgenommen.

## Legacy-Endpoints (Übergangsschicht)

Die folgenden Routen laufen seit Phase 2 als Thin Adapter und bleiben nur für UI-Kompatibilität erhalten:

- `GET /api/v1/abrain/status`
- `GET /api/v1/abrain/presets`
- `GET /api/v1/abrain/context`
- `POST /api/v1/abrain/query`

Presets (`daily_overview`, `critical_issues`, `overdue_tasks`, `sensor_attention`, `reactor_attention`, `recent_activity`) und Antwortfelder (`summary`, `highlights`, `recommended_actions`, `referenced_entities`, `used_context_sections`, `fallback_used`) bleiben formal gleich, werden aber durch den Adapter befüllt.
