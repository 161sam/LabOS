# ROADMAP

LabOS entwickelt sich zu einem modularen Operating System für EcoSphereLab.  
Der Fokus bleibt auf lokalem Betrieb, Raspberry-Pi-Tauglichkeit, klaren operativen Datenmodellen und kleinen nachvollziehbaren Erweiterungen. Die bestehende Ausrichtung bleibt erhalten und wird um eine stärkere Multi-Lab-, ReactorOps- und plattformorientierte Perspektive erweitert.

---

# Produktbild

LabOS ist nicht nur eine einzelne Labor-App, sondern das zentrale Betriebssystem für ein reales, hybrides Innovationslabor.

## Kernbereiche

- **BioOps**  
  Charges, Reaktoren, Kulturen, Sensorik, Fotos, Prozessdokumentation

- **ReactorOps**  
  Modulare Reaktorsysteme, Telemetrie, Setpoints, Schedules, Overrides, Kalibrierung, Safety, Digital Twin

- **MakerOps**  
  Werkbankgeräte, 3D-Druck, Elektronikgeräte, Fertigungsassets, Builds, Reparaturen

- **ITOps**  
  Server, SBCs, GPU-Nodes, Netzwerktechnik, Dienste, Storage, Backups

- **KnowledgeOps**  
  Wiki, SOPs, How-tos, Dev Docs, User Docs, verlinkbares Betriebswissen

- **Automation**  
  Regeln, Alerts, Tasks, nachvollziehbare Ausführungen, Dry-Runs

- **AI Assistenz**  
  ABrain auf echter LabOS-Datengrundlage statt losgelöster Demo-Logik

- **R&D Ops**  
  Projekte, Experimente, Hypothesen, Ergebnisse, Iterationen, Learnings

---

# Bereits umgesetzt

- Charges CRUD
- Reactors CRUD
- Alembic Migrationen
- Sensorik V1
- Tasks + Alerts V1
- Photo Upload + Vision Basis V1
- ABrain Integration V1 mit echtem LabOS-Kontext
- Regelengine / Automation V1
- AssetOps / DeviceOps V1
- Inventory / MaterialOps V1
- QR / Label / Traceability V1
- Rollen / Auth V1
- ReactorOps / Digital Twin V1
- Reactor Control / Telemetry V1
- MQTT / ESP32 / Pi Architektur V1
- **Calibration / Maintenance / Safety V1**
- Dashboard-Basis
- Wiki-Basis

---

# Aktueller Status: Calibration / Maintenance / Safety V1

Dieser Schritt gibt LabOS erstmals eine saubere betriebliche Sicherheits- und Vertrauensebene fuer Reaktoren, Sensoren und Nodes.

## Enthalten

- `CalibrationRecord` fuer pH, Temp, EC, Flow und andere Parameter auf Reaktoren, Nodes und Assets
- `MaintenanceRecord` fuer Reinigung, Inspektion, Austausch und Service
- `SafetyIncident` mit Typen, Schweregraden, Statuswechsel und optionalem Reaktor-/Node-Bezug
- Command-Guard-Logik: Commands werden geblockt, wenn kritische Incidents offen sind, Nodes offline sind oder Kalibrierungen abgelaufen sind
- `blocked_reason` als erklaerbares Protokollfeld am ReactorCommand
- Dashboard-KPIs: offene Incidents, faellige Kalibrierungen, ueberfaellige Wartung
- Safety-Seite `/safety` mit Incident-, Kalibrierungs- und Wartungsansicht
- Seed-Daten fuer nachvollziehbare Demo-Szenarien
- 25 Backend-Tests fuer alle neuen Endpunkte und Guard-Logik

## Verhaeltnis zu ReactorOps / Reactor Control

- ReactorOps (Digital Twin, Setpoints, Events) bleibt unveraendert
- Commands nutzen jetzt die Guard-Schicht vor dem MQTT-Publish
- Incidents koennen sich auf Reaktor-ID oder DeviceNode-ID beziehen
- Kalibrierung und Wartung sind Ziel-ID-basiert, nicht im Digital Twin modelliert

## Bewusst noch nicht enthalten

- echte Hardware-Abschaltung / GPIO-Safe-State
- ACK / Retry fuer Commands
- PID / Control Loops
- automatische Kalibrierworkflows
- MQTT-Haertung / TLS
- vollautomatische Safety-Steuerung
- Compliance-/Audit-Framework

## Grundlage fuer

- Command ACK / Retry mit Guard-Pre-Check
- Scheduler mit Guard-Bedingungen
- Vision Node
- echte Hardware-Kommandos mit Safety-Gate
- geschlossene Regelkreise mit Interlock-Bedingungen

---

# Aktueller Status: MQTT / ESP32 / Pi Architektur V1

Der aktuelle Schritt erweitert LabOS von reiner REST-basierter Reactor-Control-Struktur zu einer echten lokalen Messaging- und Node-Anbindungsschicht fuer Pi- und ESP32-nahe Betriebsablaeufe.

## Enthalten

- lokaler Mosquitto-Broker im Compose-Stack
- definierte Topic-Struktur fuer Reaktor-Telemetrie, Control, Node-Status und Heartbeats
- Python-MQTT-Bridge im API-Service mit sauberem Startup-/Shutdown-Hook
- Persistierung von MQTT-Telemetrie in `TelemetryValue`
- Upsert von Node-Status/Heartbeats in `DeviceNode`
- optionaler MQTT-Publish fuer `ReactorCommand`
- `node_id` als minimale stabile Node-Identitaet fuer DeviceNodes
- kleine UI-Sichtbarkeit fuer MQTT-Bridge-Status, Device-Node-ID und Device-originierte Telemetrie
- Beispiel-Firmware und lokaler MQTT-Simulator fuer testbare Dev-Pfade

## Bewusst noch nicht enthalten

- MQTT-Auth/TLS-Haertung
- WebSocket-Live-UI
- GPIO-, Serial- oder Firmware-Aufrufe mit echter Anlagenwirkung
- ACK / Retry
- Licht-/Temperatur-Scheduler
- Dosing- und PID-Logik
- Kalibrier-Workflows als eigenes Modul
- Safety-/Interlock-Systeme
- Incident-Automation
- Multi-Reactor-Orchestrierung

---

# Strategische Ausrichtung ab jetzt

LabOS wird schrittweise vom operativen Kern zu einem vollständigen EcoSphereLab OS erweitert.

Das bedeutet:

- reale Geräte + reale Materialien + reale Prozesse + reales Wissen
- nicht nur Dokumentation, sondern Betriebsführung
- nicht nur Bio-Lab, sondern Multi-Domain-Lab
- nicht nur Dashboards, sondern Handlungssystem
- nicht nur Daten sammeln, sondern strukturieren, steuern und verbessern

---

# Priorisierte nächste Schritte

## Priorität A – Operativer Kern

1. Inventur- / Scan-Workflow V1 vervollstaendigen
2. Asset-nahe Wartungslogik mit Alerts und Regeln
3. Verbrauchshistorie / Nachkauf-Vorbereitung auf Basis des Inventory- und Label-Modells
4. Rollen / Auth V1 zu feineren Berechtigungen, Safety-Guards und spaeterem Audit-Ausbau vorbereiten
5. MQTT-/Node-Layer an ACK, Retry, Device-Health und spaetere Safety-Guards anschlussfaehig vertiefen

---

## Priorität B – ReactorOps Ausbau

5. ReactorOps / Digital Twin V1 ✓
6. Reactor Control / Telemetry V1 ✓
7. Calibration / Maintenance / Safety V1 ✓

---

## Priorität C – EcoSphereLab Ausbau

8. ITOps / InfraOps V1
9. Sensorik V2 mit Asset- und Device-Bezug
10. Wiki-UI V2 mit tieferen Referenzen zwischen Objekten und Dokumenten
11. Experiments / R&D Ops V1

---

## Priorität D – Intelligence Layer

12. Vision V2 für strukturierte Foto-Auswertung
13. ABrain V2 Cross-Domain Assistenz
14. Predictive / Recommendation Features

---

## Priorität E – Skalierung

15. Multi-Node / Zone-Awareness V1
16. Backup / Restore / Deployment Härtung
17. Pilotnutzung außerhalb des eigenen Labs

---

# Geplante Ausbauphasen

---

## v0.2.x – Operativ starkes LabOS

Ziel:

- Geräte und Materialien integriert
- QR-fähige reale Objekte
- Rollenmodell und lokale Auth-Basis
- ReactorOps-Grundlage mit Digital Twin
- Reactor-Control-Basis mit Telemetrie, Setpoints und Devices
- MQTT-Basis fuer ESP32-/Pi-Nodes
- Wartungslogik
- erste ReactorOps-Strukturen

---

## v0.3.x – Smart LabOS

Ziel:

- Digital Twin für Reaktoren
- modulare Telemetrie
- Kalibrier- und Safety-Logik
- Cross-Domain Assistenz
- Vision-Auswertung

---

## v0.4.x – EcoSphereLab OS

Ziel:

- BioOps + ReactorOps + MakerOps + ITOps + KnowledgeOps in einem System
- mehrere Zonen / mehrere Nodes
- strukturierte Automation
- Assistenz auf Systemebene
- echtes Betriebs- und Wissenssystem

---

# ReactorOps Roadmap (neu integriert)

ALG-1-artige Systeme dienen als Inspirationsquelle für Funktionsklassen – nicht als Kopiervorlage.

LabOS übernimmt diese Fähigkeiten als Plattformmodule.

---

## ReactorOps / Digital Twin V1

Ein Reaktor wird nicht nur Stammdatensatz, sondern Prozessobjekt.

### Enthalten:

- Kulturtyp / Strain
- Volumen
- Medium / Rezept
- Inokulationsdatum
- Zielbereiche für pH / Temperatur / Licht / Flow
- Wachstumsphase
- Erntefenster
- letzte Eingriffe
- Kontaminationsereignisse
- Prozesshistorie

---

## Reactor Control / Telemetry V1

### Enthalten:

- Telemetriekanäle:
  - pH
  - Temperatur
  - Licht
  - Flow
- Setpoints
- Device- / Node-Struktur
- Command-Log / Stub-Queue
- API fuer Ingest, Latest und History
- vorbereitete spaetere ACK-/Command-Pipeline
- einfache UI fuer Werte, Setpoints und Commands

---

## MQTT / ESP32 / Pi Architektur V1

### Enthalten:

- lokaler Mosquitto-Broker
- Topic-Schema fuer:
  - Telemetrie
  - Control
  - Status
  - Heartbeat
- Python-Bridge von MQTT nach LabOS-Modell
- vorbereiteter Command-Publish von LabOS nach MQTT
- minimale Node-Identitaet mit `node_id`
- ESP32-Referenz und lokaler Simulationspfad

---

## Calibration / Maintenance / Safety V1

### Enthalten:

- Kalibrierstatus
- Kalibrierintervalle
- Wartung fällig
- Incident-Typen:
  - clogging suspicion
  - dry run risk
  - overheat
  - module fault
- Safe-State Konzepte
- automatische Wartungs-Tasks

---

# Inventory / MaterialOps Roadmap

## Bereits in V1 umgesetzt

- Materialien
- Verbrauchsgüter
- Mengen / Einheiten
- Lagerorte
- Mindestbestände
- kritische Bestände
- Asset-Zuordnung optional

## Als nächste Ausbaustufen

- Verbrauchshistorie
- Einkaufslisten
- Lieferanten
- Batch-/Lot-Tracking

---

# QR / Label / Traceability Roadmap

## Bereits in V1 umgesetzt

- Label-Codes für reale Objekte
- QR-Ziele für Assets und Inventory
- scan-fähige Browser-Zielseite
- Aktiv/Inaktiv-Status für Labels
- kleine Dashboard- und Objekt-Integration

## Als nächste Ausbaustufen

- mobile Scan-optimierte Flows
- Inventur-Unterstützung
- Zone- / Shelf- / Box-Labels
- Reactor-, Charge- und Experiment-Ziele
- Reprints / Label-Historie

---

# ITOps Roadmap

## ITOps / InfraOps V1

- Hosts
- Nodes
- Dienste
- Storage
- Backupstatus
- Rollen
- operative IT-Aufgaben

## Später:

- Container Health
- GPU Jobs
- Netzwerkdiagramme
- Auto Discovery

---

# KnowledgeOps Roadmap

## Wiki V2

- tiefe Objektverknüpfungen
- Asset ↔ SOP
- Reactor ↔ Rezept
- Task ↔ Anleitung
- Experiment ↔ Ergebnis
- Suchbarkeit verbessern

---

# ABrain Roadmap

## ABrain V2

- Cross-Domain Kontext
- Geräte + Inventory + Reaktoren + IT + Experimente
- strukturierte Empfehlungen
- Explainability
- Rule Suggestions

## Später:

- aktive Assistenz
- Voice Layer
- Multi-Agent Flows

---

# Architekturleitlinien

- modularer Monolith vor Service-Aufspaltung
- lokale Datenhaltung vor Cloud-Annahmen
- wenige klare Modelle statt generischer Meta-Systeme
- Erweiterungen entlang realer Betriebsobjekte
- Cross-Domain-Verknüpfungen explizit und nachvollziehbar halten
- Pi-Tauglichkeit bleibt Pflicht
- Safety vor Spielerei
- echte Nutzung vor theoretischer Architektur

---

# Wichtige Abgrenzungen

- Assets / Devices sind nicht dasselbe wie Inventory
- Reaktoren sind nicht nur Assets, sondern Prozesssysteme
- ABrain bleibt Assistenzschicht, nicht Primärsystem
- Automatisierung muss sichtbar, protokolliert und deaktivierbar bleiben
- Vision ersetzt keine saubere Sensorik
- jede Erweiterung muss für Raspberry Pi 4/5 praktikabel bleiben

---

# Technische Leitlinien

## Frontend

- einfache nutzbare Operator-UIs
- klare Dashboards
- mobile / Touchscreen brauchbar
- keine unnötig schwere UI-Komplexität

## Backend

- Services statt fette Router
- klare Schemas
- Alembic-first
- nachvollziehbare APIs
- Rule Engine ausbaubar halten

## Datenbank

- saubere Kernobjekte
- Indizes
- Historisierung
- Zustände explizit modellieren
- keine chaotischen Freitext-Silos

---

# Risiken

## Produkt-Risiken

- zu viele Domänen parallel
- Feature-Wildwuchs
- zu wenig echter täglicher Nutzen
- LabOS bleibt zu abstrakt

## Technische Risiken

- zu schwere Stacks für Pi
- Datenmodell driftet
- UI inkonsistent
- zu frühe Komplexität

## Gegenmaßnahmen

- kleine reale Inkremente
- jede Woche nutzbarer Fortschritt
- echte Nutzung priorisieren
- konsequentes Scope-Management

---

# Definition of Done

Ein Feature gilt als fertig, wenn:

1. Code implementiert ist
2. UI oder API sinnvoll nutzbar ist
3. Fehlerfälle berücksichtigt sind
4. Tests ergänzt wurden
5. Doku aktualisiert wurde
6. Docker/dev Setup funktioniert
7. Raspberry-Pi-Tauglichkeit mitgedacht wurde
8. Das Feature ins Gesamtmodell passt

---

# Langfristige Vision

LabOS wird das zentrale Operating System eines unabhängigen Innovationslabors.

Später möglich:

- mehrere Standorte
- mehrere Pis / Nodes
- modulare Reaktorfamilien
- Asset + Inventory + Produktion
- Vision + Assistenz + Analytics
- SOP-gesteuerte Prozesse
- digitale Laborzwillinge
- reale Pilotnutzung durch Dritte
- Produktisierung als Plattform
