# ROADMAP.md

# LabOS Roadmap

## Projektmission

LabOS ist ein modulares, Raspberry-Pi-fähiges digitales Labor-Betriebssystem für biologische, chemische, technische und experimentelle Kleinlabore.

Ziel:

- Planung
- Steuerung
- Protokollierung
- Live Monitoring
- Chargenmanagement
- Automatisierung
- Wissensmanagement
- KI Assistenz
- Vision / Kamerasysteme
- Offline First Betrieb

Langfristig soll LabOS zur führenden Open-Source-Plattform für kleine autonome Labore, Urban Farming Systeme, Fermentation Labs und modulare Forschungsumgebungen werden.

---

# Leitprinzipien

1. Offline first
2. Raspberry Pi first
3. Open Source first
4. Modular by Design
5. Automation ready
6. Human in control
7. Reproducible operations
8. Clean UX
9. API first
10. AI as assistant, not chaos

---

# Aktueller Stand

Version: v0.1.0 Bootstrap

Vorhanden:

- Next.js Frontend
- FastAPI Backend
- PostgreSQL Vorbereitung
- Docker Compose
- Dashboard Basis
- Charges Modul Basis
- Reactors Modul Basis
- Wiki Basis
- ABrain Placeholder
- Repo Struktur

---

# Versionierung

## Phase Alpha

v0.1.x = Fundament bauen

## Phase Beta

v0.2.x = reale Laborfunktionen

## Phase RC

v0.9.x = produktionsnahe Tests

## Phase Stable

v1.0.0 = produktiv nutzbar

---

# Roadmap Detail

---

# v0.1.1 Core Stabilisierung

Ziel: Bootstrap produktiv nutzbar machen

## Backend

- echte PostgreSQL Verbindung finalisieren
- Alembic Migrationen
- Logging verbessern
- Config via .env sauber

## Frontend

- Navigationslayout
- Responsive Fixes
- API Fetch Layer

## DevOps

- CI via GitHub Actions
- lint + tests
- health checks

Erfolg wenn:

- docker compose up läuft stabil
- frontend + api sauber starten

---

# v0.1.2 CRUD Complete

## Charges

- erstellen
- bearbeiten
- archivieren
- Filter
- Suche

## Reactors

- CRUD vollständig
- Reaktorstatus
- Reinigungshistorie

## Tasks

- tägliche Aufgaben
- Erinnerungen

---

# v0.1.3 Wiki Integrated

## Wiki Features

- Markdown Renderer
- Suche
- Kategorien
- Uploads
- Editor

## Inhalte

- SOPs
- How Tos
- Fehlerdatenbank
- Tutorials

---

# v0.1.4 Sensor Layer

## Unterstützte Sensoren

- Temperatur
- Luftfeuchte
- Wasser Temperatur
- pH
- EC
- Licht
- CO₂ optional

## Features

- Live Daten
- Historie
- Charts
- Grenzwerte

---

# v0.1.5 Automation Layer

## Regeln

IF temp > x THEN fan_on

## Funktionen

- Scheduler
- Rule Engine
- GPIO Steuerung
- Alerts

---

# v0.1.6 Vision Layer

## Kamera Funktionen

- Live Stream
- Snapshot
- Zeitraffer
- Wachstumserkennung
- Kontaminationswarnung

---

# v0.1.7 ABrain Integration

## KI Assistent

- Chat
- Datenanalyse
- Handlungsempfehlungen
- Wissensabfragen
- Multi-Agent Hooks

---

# v0.1.8 Reports

- PDF Reports
- Chargenberichte
- KPI Export
- CSV Export

---

# v0.2.0 Real Lab Release

Erste reale produktive Laborversion

Enthält:

- stabile Sensorik
- Automation
- Vision
- vollständige Chargenverwaltung
- Backup Restore
- Multi User
- Rollen

---

# v0.3.x Multi Node

- mehrere Raspberry Pis
- Zentrales Dashboard
- Remote Standorte
- Cluster Labs

---

# v0.5.x Marketplace

- Plugins
- Sensor Treiber
- Community Templates

---

# v1.0.0 Stable

Professionell produktiv nutzbar.

---

# Strategische Differenzierung

LabOS konkurriert nicht direkt mit:

- Home Assistant
- Excel
- Notion
- klassische ELN Systeme

LabOS verbindet:

- Laborsteuerung
- KI
- Dokumentation
- Sensorik
- Edge Computing
- Raspberry Pi

---

# Priorität aktuell (SOFORT)

1. CRUD finalisieren
2. Auth
3. Sensor Ingest
4. Dashboard live
5. Wiki besser
6. ABrain MVP
7. Backups

---

# Definition of Done je Feature

Ein Feature ist fertig wenn:

- dokumentiert
- getestet
- UI vorhanden
- API vorhanden
- stabil
- auf Pi testbar

---

# Nordstern

Ein einzelner Raspberry Pi soll ein intelligentes Mini-Labor vollständig betreiben können.
