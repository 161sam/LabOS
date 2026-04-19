# Reactor Stack

Der Reactor-Stack deckt die gesamte Kette von Stammdaten bis zur Node-Kommunikation ab:

- **ReactorOps / Digital Twin V1** — Prozessobjekt mit Phase, biologischem Zustand, technischem Zustand
- **Reactor Control / Telemetry V1** — Zeitreihen, Setpoints, Devices, Command-Queue
- **MQTT / ESP32 / Pi Architektur V1** — lokaler Broker, Topic-Schema, Bridge
- **Command ACK / Retry V1** — UID-Korrelation, ACK-Topic, Timeout, Retry

## ReactorOps / Digital Twin V1

ReactorOps erweitert LabOS von einfachem Reactor-CRUD zu geführten biologischen und technischen Prozessobjekten.

- `Reactor` bleibt Stammdatensatz (Typ, Volumen, Standort, Grundstatus).
- `ReactorTwin` bildet den laufenden Betriebszwilling (Phase, biologischer Zustand, technischer Zustand, Zielbereiche).
- `ReactorEvent` dokumentiert Inokulationen, Beobachtungen, Mediumwechsel, Wartung und Vorfälle.

**Biologische Zustände:** `stable`, `adapting`, `growing`, `stressed`, `contaminated`, `unknown`.
**Technische Zustände:** `nominal`, `warning`, `maintenance`, `degraded`, `error`.
**Prozessphasen:** `inoculation`, `growth`, `stabilization`, `harvest_ready`, `maintenance`, `paused`, `incident`.
**Kontamination:** `suspected`, `confirmed`, `recovering`, `cleared`.

### Endpoints

- `GET /api/v1/reactor-ops`, `GET /api/v1/reactor-ops/{reactor_id}`
- `POST /api/v1/reactor-ops`, `PUT /api/v1/reactor-ops/{reactor_id}`
- `PATCH /api/v1/reactor-ops/{reactor_id}/phase`
- `PATCH /api/v1/reactor-ops/{reactor_id}/state`
- `GET /api/v1/reactors/{reactor_id}/events`, `POST /api/v1/reactors/{reactor_id}/events`

### UI

- `/reactor-ops` mit Übersicht, Detail, Phasen-/State-Wechsel, Event-Historie

## Reactor Control / Telemetry V1

Reactor Control erweitert LabOS von reinem Sollzustand auf die erste Ist-/Control-Schicht.

- `TelemetryValue` — leichte Zeitreihe pro Reaktor (`temp`, `ph`, `light`, `flow`, `ec`, `co2`, `humidity`)
- `DeviceNode` — minimale Hardware-/Node-Schicht für ESP32-, Sensor-Bridge- oder Controller-Knoten
- `ReactorSetpoint` — Zielwerte und optionale Min-/Max-Korridore pro Parameter
- `ReactorCommand` — Command-Log / Stub-Queue

### Endpoints

- `POST /api/v1/telemetry`
- `GET /api/v1/reactors/{reactor_id}/telemetry`, `GET /api/v1/reactors/{reactor_id}/telemetry/latest`
- `GET /api/v1/devices`, `POST /api/v1/devices`, `PATCH /api/v1/devices/{device_id}`
- `GET /api/v1/reactors/{reactor_id}/setpoints`, `POST /api/v1/reactors/{reactor_id}/setpoints`, `PATCH /api/v1/setpoints/{setpoint_id}`
- `POST /api/v1/reactors/{reactor_id}/commands`, `GET /api/v1/reactors/{reactor_id}/commands`

Beispiel:

```bash
curl -b .labos-cookie.txt -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{"reactor_id":1,"sensor_type":"temp","value":29.8,"unit":"degC","source":"device"}'
```

### UI

- `/reactor-control` mit Werten, Setpoints, Command-Aktionen, Device-Status, MQTT-Bridge-Indikator

### Bewusst noch nicht enthalten

- PID-Regelung / Dosing-Logik
- GPIO- / Firmware-Aufrufe mit echter Anlagenwirkung
- WebSockets-Live-UI

## MQTT / ESP32 / Pi Architektur V1

Lokale Messaging-Schicht zwischen API, Pi und Edge-Nodes.

### Topic-Struktur

- `labos/reactor/{reactor_id}/telemetry/{sensor_type}`
- `labos/reactor/{reactor_id}/control/{channel}`
- `labos/reactor/{reactor_id}/ack`
- `labos/node/{node_id}/status`
- `labos/node/{node_id}/heartbeat`

### Beispiel-Payloads

Telemetry:

```json
{ "value": 29.4, "unit": "degC", "source": "device", "node_id": "esp32-a1" }
```

Node-Status:

```json
{
  "name": "ESP32 Env Node A1",
  "reactor_id": 1,
  "node_type": "env_control",
  "status": "online",
  "firmware_version": "v0.4.0"
}
```

Command-Publish aus LabOS (Topic `labos/reactor/1/control/light`):

```json
{
  "command_id": 11,
  "command_uid": "…uuid…",
  "reactor_id": 1,
  "command_type": "light_on",
  "channel": "light",
  "command": "on",
  "source": "labos"
}
```

### Referenzen

- ESP32-Firmware-Beispiel: [`examples/esp32/env_node_example.ino`](../../examples/esp32/env_node_example.ino)
- Lokaler Simulator: [`scripts/mqtt/simulate_env_node.py`](../../scripts/mqtt/simulate_env_node.py)

### Bewusst noch nicht enthalten

- MQTT-Auth / TLS / WAN-Betrieb
- WebSocket-Live-UI
- Auto-Discovery oder komplexe Device-Registry

## Command ACK / Retry V1

Macht MQTT-Commands zustellbar, bestätigbar und gezielt wiederholbar.

### ReactorCommand-Erweiterung

- `command_uid` (UUID) als Korrelations-ID für MQTT-Antworten
- `published_at`, `acknowledged_at`, `timeout_at`
- `retry_count`, `max_retries` (Default 3)
- `last_error`, `ack_payload` (JSON)
- Status-Werte: `pending`, `sent`, `acknowledged`, `failed`, `blocked`, `timeout`, `retrying`

### ACK-Flow

- Bridge abonniert `labos/reactor/{id}/ack` (Payload `{command_id, command_uid, status, error?, received_at?}`)
- `POST /api/v1/reactor-commands/{id}/retry` — inkrementiert `retry_count`, republiziert, respektiert `max_retries`
- `POST /api/v1/reactor-commands/check-timeouts` — markiert überfällige Commands als `timeout`
- Standard-ACK-Timeout: 30 s (`COMMAND_ACK_TIMEOUT_SECONDS`)

### UI

- Command-Tabelle mit ACK-Zeitstempel, Retry-Zähler, Fehlermeldungen, Retry-Button (Rolle Operator/Admin)

### Simulator

`scripts/mqtt/simulate_env_node.py` publiziert ACKs; optional mit `--ack-error-rate` für NACK-Tests.
