# LabOS

LabOS ist ein Raspberry-Pi-taugliches Labor-Betriebssystem für Planung, Protokollierung, Live-Monitoring, Wiki, Automatisierung und KI-Assistenz.

## V1 Scope

- Dashboard
- Chargenverwaltung
- Reaktorverwaltung
- Sensor-API
- Task- und Alert-Basis
- integriertes Wiki auf Markdown-Basis
- ABrain-Connector als Platzhalter
- Docker-Compose-Setup für lokale Entwicklung

## Struktur

```text
LabOS/
├── apps/frontend        # Next.js 14 Web UI
├── services/api         # FastAPI Backend
├── docs/wiki            # integriertes Markdown-Wiki
├── infra/docker         # optionale Infra-Dateien
├── configs              # Beispielkonfigurationen
└── scripts              # Hilfsskripte
```

## Schnellstart

```bash
cp .env.example .env
mkdir -p storage/wiki storage/photos

docker compose up --build
```

Danach:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Nächste Schritte

1. Auth ergänzen
2. echte Sensor-Adapter anbinden
3. Live-Daten via WebSocket ergänzen
4. ABrain-Integration aktivieren
5. Vision-Service ergänzen
6. Backup- und Rollenmodell ergänzen
