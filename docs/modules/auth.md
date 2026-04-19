# Rollen / Auth V1

Lokale Mehrnutzerbasis ohne externe Identity-Abhängigkeit.

## Enthalten

- lokales `UserAccount`-Modell mit Passwort-Hash, Rolle, Aktivstatus, letztem Login
- Login über `POST /api/v1/auth/login`
- Session-Cookie + API-Token (Browser + Skriptzugriff)
- `GET /api/v1/auth/me` für Session-Auflösung im Frontend
- `POST /api/v1/auth/logout` für lokalen Session-Clear
- Admin-verwaltete User-API unter `/api/v1/users`
- serverseitige Rollenprüfung auf kritischen Schreibpfaden

## Rollen

- **viewer** — Lesezugriff auf geschützte LabOS-Bereiche, keine kritischen Schreibaktionen
- **operator** — operative Schreibaktionen für Chargen, Reaktoren, Assets, Inventory, Labels, Fotos, Sensorwerte, Tasks, Alerts; Approval für low/medium-Risk ABrain-Actions
- **admin** — volle Kontrolle inkl. Benutzerverwaltung, Regeln, systemnaher ABrain-/Admin-Pfade, Approval für high/critical-Risk Actions

## Geschützte API-Logik

- Fast alle `/api/v1/*`-Routen verlangen Anmeldung.
- Bewusst offen bleiben nur `/`, `/healthz` und `POST /api/v1/auth/login`.
- Sensorwert-Ingest ist in V1 nicht anonym offen, sondern mindestens `operator`.
- Userverwaltung unter `/api/v1/users` ist ausschließlich `admin`.

## Bootstrap

Beim ersten Start bootstrapped LabOS genau einen lokalen Admin nur dann, wenn in `useraccount` noch kein Benutzer vorhanden ist. Credentials stehen in den `BOOTSTRAP_ADMIN_*`-Variablen.

Lokaler Login:

```bash
curl -c .labos-cookie.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"labosadmin"}'

curl -b .labos-cookie.txt http://localhost:8000/api/v1/auth/me
```

## Bewusst noch nicht enthalten

- OAuth / OIDC / SSO
- LDAP
- Passwort-Reset per Mail
- 2FA
- Multi-Tenant- oder Teammodell
- feingranulare Objektberechtigungen
- serverseitige Token-Revocation-Liste
