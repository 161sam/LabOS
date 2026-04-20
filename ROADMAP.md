# 🚀 LABOS ROADMAP (UPDATED – ROS + ABrain ALIGNMENT)

---

# 🧠 Produktbild

LabOS entwickelt sich zu einem **modularen Operating System** für EcoSphereLab.  


Es verbindet:

* biologische Systeme (BioOps)
* technische Systeme (ReactorOps)
* Fertigung (MakerOps)
* IT-Infrastruktur (ITOps)
* Wissen (KnowledgeOps)
* Automation & Safety
* robotische Systeme (RobotOps – neu)

---

# 🧭 Zielarchitektur (final definiert)

```text
Smolit-AI-Assistant
        ↓
      ABrain
        ↓
LabOS MCP Server / Tool Adapter
        ↓
LabOS API / DB / Domain / Guards / State
        ↓
ROS Compatibility Layer (Robot Runtime Bridge)
        ↓
Reactor Nodes / Hydro Nodes / Vision Nodes / Robot Systems
```

---

## Rollenverteilung

### LabOS

* beschreibt Realität (State)
* führt Aktionen aus (Execution)
* erzwingt Safety / Domain Guards
* speichert Daten
* bietet Tool/API Surface

### ABrain

* plant
* entscheidet
* orchestriert
* verwaltet Governance / Approval / Trace

### Smolit-AI-Assistant

* User Interface
* Kommunikation mit Menschen

### ROS Layer (neu)

* Echtzeit-Execution
* Robot Nodes / Topics / Actions
* Hardware-nahe Steuerung

---

## Entscheidungsregel

* LabOS kontrolliert die Realität
* ABrain entscheidet über Aktionen
* ROS führt physische Aktionen aus
* der Assistant spricht mit dem Nutzer

---

# ✅ Bereits umgesetzt (Stand jetzt)

## Core

* Charges CRUD
* Reactors CRUD
* Sensorik V1
* Tasks + Alerts V1
* Rule Engine V1
* Dashboard Basis
* Wiki Basis

## Operations

* AssetOps / DeviceOps V1
* Inventory / MaterialOps V1
* QR / Label / Traceability V1
* Rollen / Auth V1

## ReactorOps

* Digital Twin V1
* Reactor Control / Telemetry V1
* MQTT / ESP32 / Pi Architektur V1
* Calibration / Maintenance / Safety V1
* Command ACK / Retry V1
* Scheduler / Automation Runtime V1
* Vision Node / AI Integration V1
* Sensor + Vision Fusion / Reactor Health V1

## ABrain Integration

* Adapter Alignment V1 (Phase 1–3)
* Boundary Hardening V1
* Approval System V1
* Trace / Audit Layer V1

---

# 📍 Aktueller Systemzustand

LabOS ist jetzt:

👉 **ein voll funktionsfähiges, lokales cyber-physisches Betriebssystem**

mit:

* Telemetrie
* Commands
* Scheduling
* Safety Guards
* Approval (HITL)
* Trace/Audit
* Vision + Health
* MQTT Node-System
* ABrain Adapter
* ROS + MQTT Hybrid
* ABrain V2 Integration Surface (`/abrain/adapter/reason`, Decision Surface UI)

---

# 🔥 Nächste große Entwicklungsphase

---

# 🧩 PHASE 1 — MCP SERVER V1

## Ziel

LabOS wird vollständig als Tool-System für ABrain nutzbar.

## Enthalten

* MCP Server (Model Context Protocol)
* Tool Registry
* Context Exposure
* Action Execution via MCP
* Auth für ABrain Zugriff
* Trace Integration

## Ergebnis

👉 LabOS ist offiziell “steuerbar” durch ABrain

---

# 🤖 PHASE 2 — ROS COMPATIBILITY LAYER V1 (NEU)

## Ziel

LabOS wird kompatibel mit **Robot Operating System (ROS2)**

## Motivation

Alle Systeme werden als **robotische Einheiten** modelliert:

* Reaktoren
* Hydro-Systeme
* Sampling Nodes
* Vision Nodes
* Werkstattgeräte
* zukünftige mobile Roboter

---

## Enthalten

### 1. ROS Bridge Service

* MQTT ↔ ROS Bridge
* LabOS API ↔ ROS Topics

### 2. Mapping Layer

| LabOS          | ROS              |
| -------------- | ---------------- |
| DeviceNode     | ROS Node         |
| TelemetryValue | Topic            |
| ReactorCommand | Action / Service |
| ReactorHealth  | State Topic      |
| SafetyIncident | Diagnostic Topic |

---

### 3. Node Lifecycle Mapping

* online / offline → ROS lifecycle
* heartbeat → node status

---

### 4. Erste ROS Node Typen

* env_node
* sampling_node
* dosing_node
* vision_node
* hydro_node

---

## Ergebnis

👉 LabOS wird **RobotOS-kompatibel**

👉 Reaktoren = robotische Systeme

---

# 🏭 PHASE 3 — ROBOTOPS / AUTONOMOUS MODULE MODEL V1

## Ziel

Alle physischen Systeme als einheitliche robotische Einheiten modellieren

---

## Klassen

### A — Prozesssysteme

* Bioreaktoren
* Hydroponiksysteme

### B — Perception Systeme

* Kameras
* Mikroskope

### C — Fertigungssysteme

* 3D Drucker
* CNC

### D — Mobile Systeme (später)

* Transportroboter
* Manipulatoren

---

## Features

* gemeinsames Zustandsmodell
* gemeinsame Command-Schnittstellen
* Lifecycle
* Health + Safety Integration
* Multi-Node Orchestrierung

---

## Ergebnis

👉 Lab wird zu einem **robotischen Ökosystem**

---

# 🧠 PHASE 4 — ABRAIN V2 DOMAIN REASONING

## Wichtig

👉 passiert **NICHT in LabOS**

---

## Ziel

ABrain nutzt LabOS als Tool-System für echte Entscheidungslogik

---

## Fähigkeiten

### Reactor Intelligence

* Trends
* Anomalien
* Wachstumsanalyse

### Daily Ops

* Tagesplanung
* Tasks
* Routinen

### Incident Review

* Ursachenanalyse

### Maintenance Suggestions

* Wartungsempfehlungen

### Cross-Domain Reasoning

* Bio + IT + Maker + Inventory

---

## Ergebnis

👉 echtes “Brain” entsteht — **außerhalb von LabOS**

---

## Begleitend in LabOS: ABrain V2 Integration Surface

* LabOS liefert die Decision Surface unter `/abrain`, **ohne** selbst zu reasonieren.
* Neue Route `POST /api/v1/abrain/adapter/reason` ist ein **thin proxy** auf die fünf ABrain-V2-Use-Cases (`reactor_daily_overview`, `incident_review`, `maintenance_suggestions`, `schedule_runtime_review`, `cross_domain_overview`).
* Response Shape V2 (`prioritized_entities`, `recommended_actions`, `recommended_checks`, `approval_required_actions`, `blocked_or_deferred_actions`, …) wird operator-tauglich dargestellt.
* Approval / Execution / Trace bleiben LabOS-seitig maßgeblich und sind direkt aus jeder Empfehlung heraus aufrufbar (`/api/v1/abrain/execute`, `/approvals`, `/executions`, `/traces`).
* Quick Entries: Safety → `incident_review`, ReactorOps → `reactor_daily_overview`, Schedules → `schedule_runtime_review`.
* Lokale Fallback-Logik behält die V2-Shape bei (`fallback_used=true`), so bleibt die UI kohärent, auch wenn ABrain nicht erreichbar ist.

---

# 🧠 PHASE 5 — EXECUTION INTELLIGENCE

## Ziel

ABrain wird aktiv steuernd

---

## Features

* automatische Action Chains
* Multi-Step Plans
* adaptive Entscheidungen
* Feedback-Loops

---

# 📊 PHASE 6 — OPERATIONAL DEPTH

## Inventory V2

* Verbrauchshistorie
* Einkaufsvorschläge
* Batch Tracking

## ITOps V1

* Nodes
* Services
* GPU Jobs
* Netzwerk

## KnowledgeOps V2

* tiefe Verlinkung
* SOP Integration

---

# 🌐 PHASE 7 — SCALE

## Multi-Node / Zone Awareness

* mehrere Räume
* mehrere Systeme
* Netzwerkstruktur

## Deployment

* Backup
* Restore
* Versioning

## externe Nutzung

* Pilotkunden
* Plattformisierung

---

# 🧪 PHASE 8 — ADVANCED SYSTEMS

## Vision V2

* ML Modelle
* Segmentierung
* Kontaminationsdetektion

## Predictive Systems

* Forecasting
* Growth Models

## Autonomous Lab

* minimale menschliche Eingriffe

---

# 🧱 Architekturleitlinien

* LabOS ist **kein Brain**
* keine doppelte Entscheidungslogik
* Safety bleibt lokal
* alles ist auditierbar
* Pi-tauglich
* reale Nutzung > Theorie

---

# ⚠️ Risiken

* zu schnelle Komplexität
* ROS Overengineering
* ABrain und LabOS vermischen
* Hardware ohne Safety
