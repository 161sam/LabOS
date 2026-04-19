# Operational Core

Die operative Grundschicht aus Chargen, Reaktoren, Sensoren, Tasks, Alerts und Regeln. Diese Module sind die Basis — alles Tiefergehende (ReactorOps, Safety, Vision, ABrain) baut darauf auf.

## Charges & Reactors

### CRUD-Oberfläche

Die Weboberfläche unter `/charges` und `/reactors` bietet:

- Listenansicht mit Kernfeldern
- Anlegen neuer Chargen und Reaktoren
- Bearbeiten bestehender Datensätze
- direkten Statuswechsel aus der Liste
- sichtbare Loading- und Fehlerzustände

### Endpoints

- `GET/POST /api/v1/charges`, `GET/PUT /api/v1/charges/{id}`, `PATCH /api/v1/charges/{id}/status`
- `GET/POST /api/v1/reactors`, `GET/PUT /api/v1/reactors/{id}`, `PATCH /api/v1/reactors/{id}/status`

### Kernfelder

- **Charge:** `name`, `species`, `status`, `reactor_id`, `start_date`, `volume_l`, `notes`
- **Reactor:** `name`, `reactor_type`, `status`, `volume_l`, `location`, `last_cleaned_at`, `notes`

Für Prozess-/Twin-Informationen siehe [Reactor Stack](reactor-ops.md).

## Sensorik V1

Erste Sensordaten direkt in PostgreSQL, ohne zusätzliche Time-Series-DB.

### Endpoints

- `GET /api/v1/sensors`, `GET /api/v1/sensors/overview`, `GET /api/v1/sensors/{id}`
- `POST /api/v1/sensors`, `PUT /api/v1/sensors/{id}`, `PATCH /api/v1/sensors/{id}/status`
- `POST /api/v1/sensors/{id}/values`, `GET /api/v1/sensors/{id}/values`

### Felder

- **Sensor:** `name`, `sensor_type`, `unit`, `status`, `reactor_id`, `location`, `notes`, `created_at`, `updated_at`
- **SensorValue:** `sensor_id`, `value`, `recorded_at`, `source`

### Enums

- `sensor_type`: `temperature`, `humidity`, `water_temperature`, `ph`, `ec`, `light`, `co2`
- `status`: `active`, `inactive`, `error`, `maintenance`

Beispiel:

```bash
curl -b .labos-cookie.txt -X POST http://localhost:8000/api/v1/sensors/1/values \
  -H "Content-Type: application/json" \
  -d '{"value": 23.7, "source": "manual"}'
```

## Tasks + Alerts V1

Operative Arbeitsschritte und Laborhinweise direkt im System.

### Tasks

**Endpoints:** `GET/POST /api/v1/tasks`, `GET/PUT /api/v1/tasks/{id}`, `PATCH /api/v1/tasks/{id}/status`.

**Felder:** `title`, `description`, `status`, `priority`, `due_at`, `charge_id`, `reactor_id`, `asset_id`, `created_at`, `updated_at`, `completed_at`.

**Status:** `open`, `doing`, `blocked`, `done`.
**Prioritäten:** `low`, `normal`, `high`, `critical`.

### Alerts

**Endpoints:** `GET/POST /api/v1/alerts`, `GET /api/v1/alerts/{id}`, `PATCH /api/v1/alerts/{id}/ack`, `PATCH /api/v1/alerts/{id}/resolve`.

**Felder:** `title`, `message`, `severity`, `status`, `source_type`, `source_id`, `created_at`, `acknowledged_at`, `resolved_at`.

**Severity:** `info`, `warning`, `high`, `critical`.
**Status:** `open`, `acknowledged`, `resolved`.

### UI-Flows

- `/tasks` bietet Liste, Filter, Create/Edit, Statuswechsel
- `/alerts` zeigt offene und historische Alerts, erlaubt Anlegen, Ack und Resolve
- Dashboard zeigt offene Tasks, heute fällige Tasks, kritische Alerts, letzte Alerts

## Regelengine / Automation V1

Einfache, kontrollierte Regeln gegen aktuelle Systemdaten, die Tasks oder Alerts erzeugen.

### Trigger

`sensor_threshold`, `stale_sensor`, `overdue_tasks`, `reactor_status`.

### Conditions

`threshold_gt`, `threshold_lt`, `age_gt_hours`, `count_gt`, `status_is`.

### Actions

`create_alert`, `create_task`.

### Endpoints

- `GET/POST /api/v1/rules`, `GET/PUT /api/v1/rules/{id}`, `PATCH /api/v1/rules/{id}/enabled`
- `POST /api/v1/rules/{id}/evaluate` (Query-Param `dry_run=true` möglich)
- `GET /api/v1/rules/{id}/executions`, `GET /api/v1/rules/executions`
- `POST /api/v1/rules/evaluate-all`

Execution-Status: `matched`, `not_matched`, `executed`, `failed`.

### Boundary

Die Rule Engine ist **Local Automation / Fallback** (siehe [architecture.md](../architecture.md)). Jede `RuleExecution` trägt `action_result.execution_origin = 'labos_local'`. Rules sind nicht der Zielpfad — ABrain entscheidet im Zielbild, ob ein Task/Alert entstehen soll.

### V1-Grenzen

- keine Hardware-Aktionen
- keine Notifications
- keine Multi-Step-Workflows
- keine versteckte Scheduler-Magie (Scheduler-Trigger explizit in [scheduler.md](scheduler.md))

### UI

`/rules` mit Regelliste, Bearbeitung, Enable-Toggle, Dry-Run, echte Ausführung, letzte Execution-Logs.
