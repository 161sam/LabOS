# Calibration / Maintenance / Safety V1

Diese Schicht schafft die Sicherheits- und Betriebsgrundlage für reaktornahe Steuerung.

## Kalibrierung (`CalibrationRecord`)

- Zustände: `valid`, `due`, `expired`, `failed`, `unknown`
- Zieltypen: `reactor`, `device_node`, `asset`
- Parameter-basiert (pH, Temp, EC, Flow usw.)

**Endpoints**

- `GET/POST /api/v1/calibration`
- `PATCH /api/v1/calibration/{id}`
- `GET /api/v1/calibration/overview`

## Wartung (`MaintenanceRecord`)

- Typen: `cleaning`, `inspection`, `replacement`, `tubing_flush`, `filter_change`, `pump_service`, `general_service`
- Status: `scheduled`, `done`, `overdue`, `skipped`

**Endpoints**

- `GET/POST /api/v1/maintenance`
- `PATCH /api/v1/maintenance/{id}`
- `GET /api/v1/maintenance/overview`

## Safety Incidents (`SafetyIncident`)

- Typen: `calibration_expired`, `node_offline`, `dry_run_risk`, `clogging_suspected`, u. a.
- Schweregrade: `info`, `warning`, `high`, `critical`
- Status: `open`, `acknowledged`, `resolved`

**Endpoints**

- `GET/POST /api/v1/safety/incidents`
- `PATCH /api/v1/safety/incidents/{id}`
- `GET /api/v1/safety/overview`

## Command-Guard-Logik

Reactor-Commands werden vor dem MQTT-Publish serverseitig geprüft. Safety ist in LabOS die **einzige** Autorität, die Commands blockieren darf (siehe [architecture.md](../architecture.md)). Blockiergründe:

- kritischer offener Incident
- offline/error Node für sicherheitssensitive Commands
- `dry_run_risk`-Incident für Pumpe/Aeration
- abgelaufene Kalibrierung für Sample-Capture

Geblockte Commands bekommen `status=blocked` und `blocked_reason` mit Prefix `safety_guard:` (damit die Absicht im API-Response sichtbar bleibt).

## UI

- `/safety` mit Tabs Incidents, Kalibrierung, Wartung
- Dashboard-KPIs: offene Incidents, fällige/abgelaufene Kalibrierungen, überfällige Wartung

## Bewusst noch nicht enthalten

- echte Hardware-Abschaltung / GPIO-Safe-State
- automatische Kalibrier-Workflows
- MQTT-Härtung / TLS
- Compliance-/Audit-Framework
- vollautomatische Safety-Steuerung
