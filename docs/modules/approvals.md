# Approval System V1

HITL-Queue + State + UI + Audit für approval-pflichtige ABrain-Aktionen. Baut auf [ABrain Adapter Phase 3](abrain-adapter.md#phase-3--execution--governance-flow) auf — nutzt die `pending_approval`-Semantik und ergänzt den operativen Release-Pfad.

## Kernprinzip

**Approval ist Release, nicht Safety-Bypass.** `approvals.approve_request` ruft `abrain_execution.execute_action(..., approve=True)` erneut auf — Role- und Safety-Guards werden dort erneut geprüft. Blockiert es dort (z. B. `safety_guard:`-Prefix), landet das als `ApprovalRequest.status='failed'` mit `blocked_reason` im Audit.

LabOS baut damit **keinen zweiten Governance-Layer**. Planung, Multi-Step-Workflows, Delegation und Notifications bleiben bei ABrain/Smolit.

## Modell

`ApprovalRequest` (Migration `20260419_0019`, 22 Felder):

- `action_name`, `action_params` (JSON), `risk_level`
- `requested_by_source` (`abrain` | `local_dev_fallback` | `operator`)
- `requested_by_user_id`, `requested_via` (`adapter` | `legacy_query` | `future_mcp` | `operator_ui`)
- `trace_id`, `reason`
- `status` (`pending` | `approved` | `rejected` | `executed` | `failed` | `cancelled`)
- `decision_note`, `approved_by_user_id`, `decided_at`
- `executed_execution_log_id` (FK auf `ABrainExecutionLog`), `blocked_reason`, `last_error`
- `created_at`, `updated_at`

Indizes auf `status`, `action_name`, `trace_id`, `requested_by_source`, `created_at`.

## Rollenlogik

Die Rollenprüfung liegt im Service (`_ensure_decision_role`), nicht am Router — dieselbe Regel gilt auch bei zukünftigen Aufrufwegen:

- **viewer** → 403 bei Approve/Reject
- **operator** → darf low- und medium-Risk entscheiden
- **admin** → darf alles (inkl. high/critical)

## Pipeline

1. ABrain ruft `POST /api/v1/abrain/execute` mit einer Action, die `requires_approval=True` trägt.
2. `execute_action` erkennt fehlendes `approve=True` → `pending_approval`-Branch legt `ApprovalRequest` an (Status `pending`) und gibt `approval_request_id` im `ABrainExecutionResult` zurück.
3. Operator/Admin entscheidet über `/approvals`-UI oder API.
4. `approve_request` → re-invoke `execute_action(..., approve=True, source=f'approval:{username}')` → Ergebnis wird auf `status` gemapped (`executed`, `failed`, `rejected`, `blocked`) und `executed_execution_log_id` verlinkt.

## Endpoints

- `GET /api/v1/approvals` (Filter: `status`, `action_name`, `requested_by_source`, `trace_id`)
- `GET /api/v1/approvals/overview`
- `GET /api/v1/approvals/{request_id}`
- `POST /api/v1/approvals/{request_id}/approve`
- `POST /api/v1/approvals/{request_id}/reject`

Request-Payload für Approve/Reject:

```json
{ "decision_note": "optional text" }
```

## UI

`/approvals` (Route `apps/frontend/app/approvals/page.tsx`, Component `ApprovalsManager.tsx`):

- Overview-KPIs: `pending`, `high_risk_pending`, `executed`, `failed`, `rejected`
- Filter nach Status (Default `pending`) und Trace-ID
- Tabelle mit Action, Risk-Badge, Status-Badge, Quelle, Angefragt-von, Entscheider
- Detail-Card mit Parametern, Decision-Note-Textarea, Approve/Reject-Buttons
- UI-Rolle-Gating: viewer sieht `InlineMessage`, high/critical zeigt Warnung wenn nicht Admin

## Tests

`services/api/tests/test_approvals_api.py` deckt ab:

- pending-Eintrag wird angelegt, **keine Seiteneffekte**
- approve → führt aus und verlinkt `ABrainExecutionLog`
- reject → keine Ausführung
- already-decided → 409
- safety-guard blockt noch nach Approval → `status=failed` mit `blocked_reason`
- viewer → 403; high-risk → operator 403 / admin ok
- Filter-Kombinationen, Overview-Counts
- unmapped Action erzeugt keinen Approval-Request

## Noch offen

- externer Approval-Pfad durch ABrain selbst (z. B. über Smolit-Chat-UI)
- UI-Tiefenlink `approval_request_id` ↔ `ABrainExecutionLog`-History
- Audit-Export (z. B. CSV/JSON über Zeitraum)
