# Scheduler / Automation Runtime V1

Zeitbasierte Automation im LabOS-Monolithen — ohne externen Scheduler (Celery, k8s CronJob usw.).

## Schedule-Modell

- `schedule_type`: `interval`, `cron` (5-Feld Minute/Stunde/Tag/Monat/Wochentag) oder `manual`
- `target_type`: `command` (Reactor-Command über den Safety-Guard-Pfad) oder `rule` (Rule-Evaluation)
- `target_params` (JSON): z. B. `command_type` für Command-Schedules, `dry_run` für Rule-Schedules
- Laufzeitfelder: `last_run_at`, `next_run_at`, `last_status`, `last_error`

## ScheduleExecution-Log

- `status`: `success` | `failed` | `skipped`
- `trigger`: `scheduler` | `manual`
- Start/Finish, Ergebnis-JSON, Fehler
- Pro Schedule werden die jüngsten 100 Ausführungen aufbewahrt

## Runtime

- `SchedulerRunner` läuft als Daemon-Thread im FastAPI-Lifespan.
- Tick alle `scheduler_tick_seconds` (Default 5 s).
- Fällige Schedules werden sequentiell ausgeführt; Fehler pro Schedule werden geloggt, aber brechen den Tick nicht ab.
- `scheduler_enabled` und `scheduler_tick_seconds` sind über `.env` konfigurierbar.

## Boundary

Der Scheduler ist **Execution Only** — er triggert konfigurierte Targets und trifft keine Entscheidungen (siehe [architecture.md](../architecture.md)). Reactor-Commands laufen durch denselben Safety-Guard-Pfad wie manuell erstellte Commands.

## Endpoints

- `GET/POST /api/v1/schedules`
- `PATCH /api/v1/schedules/{id}`, `PATCH /api/v1/schedules/{id}/enabled`
- `DELETE /api/v1/schedules/{id}`
- `GET /api/v1/schedules/{id}/executions`
- `POST /api/v1/schedules/{id}/run`

Writes sind Operator/Admin, Reads authenticated.

## UI

- `/schedules` mit Formular, Übersichtstabelle, Enable/Disable, Manuell-Run und Ausführungshistorie

## Seed-Beispiele (initial deaktiviert)

- Lichtzyklus Reaktor A1 (Interval 12 h, `light_on`)
- Regel-Check alle 60 s (Rule „Sensor ohne Werte 24h")
- Telemetrie-Sampling-Trigger (Interval 5 min, `sample_capture`)
- Wartungscheck täglich (Cron `0 7 * * *`, Rule Dry-Run)

## Bewusst noch nicht enthalten

- verteilte Worker / Parallelausführung
- vollständige Cron-Syntax (Nicknames, L/W/#, Sekunden)
- DAG-/Workflow-Orchestrierung
- übergeordneter Retry-Controller für fehlgeschlagene Schedule-Runs
