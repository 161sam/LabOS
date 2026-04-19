# Sensor + Vision Fusion / Reactor Health V1

Diese Schicht fusioniert numerische Telemetrie, Vision-Analysen und offene Safety-Incidents zu einer strukturierten Reactor-Health-Bewertung pro Reaktor. Die Logik bleibt bewusst regelbasiert (keine ML).

## Modell

`ReactorHealthAssessment`:

- `reactor_id`, `status`, `summary`
- `signals` (JSON-Array)
- `source_telemetry_at`, `source_vision_analysis_id`, `source_incident_count`
- `assessed_at`, `created_at`
- Migration `20260419_0017_sensor_vision_fusion_v1`

**Statuswerte:** `nominal`, `attention`, `warning`, `incident`, `unknown`.

## Fusion-Service

`services/api/app/services/reactor_health.py`:

- Liest je Reaktor neueste Telemetrie pro Sensor-Typ, letzte erfolgreiche `VisionAnalysis`, offene `SafetyIncident`s, `ReactorTwin` / `ReactorSetpoint`-Zielbereiche.
- Deterministische Regeln, keine Gewichte, keine Statistik.
- Telemetrie-Signale: fehlend, veraltet (> 6 h), unter/über Zielbereich, nominal.
- Vision-Signale: Kontaminationsverdacht, zu dunkel/hell, Grünanteil niedrig, `low_sharpness`, `low_confidence`.
- Safety-Signale: kritischer / hoher / allgemeiner offener Incident.
- Statusableitung: `incident > warning > attention > nominal`. `unknown` nur wenn gar keine Daten vorliegen.

## Boundary

Reactor-Health ist **Classification + Signal Emission** (siehe [architecture.md](../architecture.md)). Der Status ist ein Label, kein Entscheid; es werden weder Tasks noch Commands automatisch erzeugt.

## Endpoints

- `GET /api/v1/reactor-health` — neueste Bewertung pro Reaktor
- `GET /api/v1/reactor-health/{reactor_id}` — aktuelle Bewertung
- `GET /api/v1/reactor-health/{reactor_id}/history` — Historie (Default 20)
- `POST /api/v1/reactor-health/{reactor_id}/assess` — neue Bewertung (Operator)

## Integrationen

- `ReactorTwinRead.latest_health` liefert Summary + Signale
- ABrain-Kontext (`reactors`-Section): `health_status`, `health_summary`, `health_assessed_at` (Sortierung priorisiert `incident > warning > attention > unknown > nominal`)
- Dashboard-KPIs: `reactors_health_nominal/attention/warning/incident/unknown`
- Auto-Trigger: nach erfolgreichem Photo-Upload mit Reaktorzuordnung wird automatisch eine Neu-Bewertung ausgeführt

## UI

- `/reactor-ops`: Health-Badge in Übersicht, Detail-Card mit Summary + Signal-Liste, "Neu bewerten"-Button
- Dashboard: Reactor-Health-KPI-Reihe (Nominal, Auffällig/Warnung, Incident)

## Bewusst noch nicht enthalten

- ML-Modelle, Gewichtungen, Zeitreihen-Analyse
- Vorhersage / Trendanalyse
- automatische Steuerungs-Eingriffe basierend auf Health-Status
- Aggregation über mehrere Reaktoren / Zonen / Lab-weite Indizes
