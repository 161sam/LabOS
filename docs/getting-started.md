# Getting Started

## Voraussetzungen

- Docker + Docker Compose
- Optional für lokale API-Entwicklung ausserhalb Docker: Python 3.11+, Node 20+

## Schnellstart mit Docker Compose

```bash
cp .env.example .env
mkdir -p storage/wiki storage/photos
docker compose up --build
```

Danach erreichbar:

- Frontend: <http://localhost:3000>
- API: <http://localhost:8000>
- API Docs (Swagger): <http://localhost:8000/docs>
- MQTT Broker: `mqtt://localhost:1883`
- MQTT over WebSockets: `ws://localhost:9001`

Beim API-Start werden zuerst Alembic-Migrationen bis `head` ausgeführt. Danach ergänzt der Seed-Flow nur fehlende Demo-Daten (Charges, Assets, Inventory, Labels, Wiki, Sensoren, Tasks, Alerts, Regeln).

## Bootstrap-Login

Beim ersten Start wird genau ein lokaler Admin angelegt, sofern in `useraccount` noch kein Benutzer vorhanden ist. Die Credentials stehen in den `BOOTSTRAP_ADMIN_*`-Variablen in `.env`.

```bash
curl -c .labos-cookie.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"labosadmin"}'

curl -b .labos-cookie.txt http://localhost:8000/api/v1/auth/me
```

Alle weiteren API-Aufrufe benötigen entweder das Session-Cookie oder einen API-Token.

## Relevante `.env`-Variablen

Auth / Rollen:

- `AUTH_SECRET_KEY`, `AUTH_COOKIE_NAME`, `AUTH_COOKIE_SECURE`, `AUTH_TOKEN_TTL_HOURS`
- `BOOTSTRAP_ADMIN_USERNAME`, `BOOTSTRAP_ADMIN_PASSWORD`, `BOOTSTRAP_ADMIN_DISPLAY_NAME`, `BOOTSTRAP_ADMIN_EMAIL`

MQTT:

- `MQTT_ENABLED`, `MQTT_BROKER_HOST`, `MQTT_BROKER_PORT`
- `MQTT_CLIENT_ID`, `MQTT_TOPIC_PREFIX`, `MQTT_PUBLISH_COMMANDS`

ABrain-Adapter:

- `ABRAIN_ENABLED`, `ABRAIN_MODE`, `ABRAIN_USE_LOCAL_FALLBACK`
- `ABRAIN_BASE_URL`, `ABRAIN_TIMEOUT_SECONDS`, `ABRAIN_USE_STUB`
- `ABRAIN_ADAPTER_CONTRACT_VERSION`

QR-/Label-Ziele:

- `PUBLIC_WEB_BASE_URL` (Default `http://localhost:3000`)
- `PUBLIC_API_BASE_URL` (Default `http://localhost:8000`)

## Persistenz-Hinweise

- `storage/photos` und `storage/wiki` sollten persistent gehalten werden (Volume in Docker).
- Die Datenbank speichert nur Metadaten; manuell gelöschte Fotos hinterlassen tote Referenzen.
- `configs/` enthält Beispielkonfigurationen und `.example`-Dateien — keine Secrets.

## Nächste Schritte

- [Development](development.md) — lokale Python-/Node-Entwicklung, Tests, Migrationen
- [Architecture](architecture.md) — was liegt wo
- [Module-Index](modules/) — Details pro Fachmodul
