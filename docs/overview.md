# Overview

LabOS ist ein Raspberry-Pi-taugliches Operating System für ein reales, hybrides Innovationslabor (EcoSphereLab). Es verbindet BioOps, ReactorOps, MakerOps, ITOps, KnowledgeOps, Automation und AI-Assistenz in einem lokal betreibbaren modularen Monolithen.

## Produktbild

LabOS ist nicht nur eine Labor-App, sondern das zentrale Betriebssystem für ein reales Lab:

- **BioOps** — Charges, Reaktoren, Kulturen, Sensorik, Fotos, Prozessdokumentation
- **ReactorOps** — Reaktorsysteme, Telemetrie, Setpoints, Schedules, Overrides, Kalibrierung, Safety, Digital Twin
- **MakerOps** — Werkbankgeräte, 3D-Druck, Elektronik, Fertigungsassets, Builds, Reparaturen
- **ITOps** — Server, SBCs, GPU-Nodes, Netzwerktechnik, Dienste, Storage, Backups
- **KnowledgeOps** — Wiki, SOPs, How-tos, Dev Docs, verlinkbares Betriebswissen
- **Automation** — Regeln, Alerts, Tasks, nachvollziehbare Ausführungen, Dry-Runs
- **AI-Assistenz** — LabOS ist nicht selbst das Brain (siehe [Architecture](architecture.md)).

## Leitprinzipien

- **Local first** — lokaler Betrieb muss jederzeit möglich bleiben, keine Cloud-Annahmen.
- **Pi-tauglich** — jede technische Entscheidung berücksichtigt Raspberry Pi 4/5.
- **Modularer Monolith** — saubere Services statt vorschneller Microservice-Zerlegung.
- **Safety vor Spielerei** — Safety-/Domain-Guards sind lokal und verbindlich.
- **Echte Nutzung vor theoretischer Architektur** — kleine reale Inkremente.

## V1 Feature-Scope

LabOS V1 bringt folgende Module mit (Details pro Modul unter [`modules/`](modules/)):

**Domain Core**
- Chargen- und Reaktorverwaltung (Create/Edit/Statuswechsel)
- Sensorik mit Werte-Ingest und Verlauf
- Tasks und Alerts mit operativen Dashboards
- Foto-Upload mit lokalem Storage
- Wiki auf Markdown-Basis
- Rollen/Auth mit lokalen Benutzerkonten

**Operational Objects**
- AssetOps / DeviceOps (Geräte, Wartungsfelder)
- Inventory / MaterialOps (Bestände, Lagerorte, Mindestmengen)
- QR / Label / Traceability (scan-fähige Objektverknüpfung)

**ReactorOps Stack**
- ReactorOps / Digital Twin (Phase, Zielkorridore, Events)
- Reactor Control / Telemetry (Zeitreihen, Setpoints, Devices, Commands)
- MQTT / ESP32 / Pi-Architektur (lokaler Broker, Topic-Schema, Bridge)
- Command ACK / Retry (UID, ACK-Topic, Timeout, Retry)
- Calibration / Maintenance / Safety (Command-Guards, Incident-Tracking)
- Scheduler / Automation Runtime (interval/cron/manual)
- Vision Node / AI Integration (Pillow-basierte Auto-Analyse)
- Sensor + Vision Fusion / Reactor Health (deterministische Status-Fusion)

**AI Boundary Layer**
- Boundary Hardening (Signal- statt Entscheidungs-Prinzip)
- ABrain Adapter Alignment (Phase 1–3: Context Builder, Action Catalog, Execution Pipeline)
- Approval System (HITL-Queue für approval-pflichtige Actions)

Der vollständige Roadmap-Kontext liegt in [ROADMAP.md](../ROADMAP.md).

## Was LabOS bewusst NICHT ist

- kein eigenes Brain (dafür ist **ABrain** vorgesehen)
- kein Chat-System (dafür ist der **Smolit-AI-Assistant** vorgesehen)
- keine ERP-/Warenwirtschaft
- kein Compliance-/Audit-Framework
- keine Multi-Tenant-Plattform
- kein Ersatz für saubere Sensorik durch Vision

Siehe [Architecture](architecture.md) für die Abgrenzung zwischen LabOS, ABrain und Smolit.
