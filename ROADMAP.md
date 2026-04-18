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
- Dashboard-Basis
- Wiki-Basis

---

# Aktueller Status: Rollen / Auth V1

Der aktuelle Schritt macht LabOS von einem offenen Einzelplatz-Prototypen zu einer ersten kontrollierten Mehrnutzerbasis fuer reale operative Labordaten.

## Enthalten

- lokales User-Modell mit Passwort-Hash, Rollen und Aktivstatus
- Login-Flow fuer Frontend und API
- Bootstrap-Admin nur bei leerer User-Tabelle
- Schutz fast aller `/api/v1/*`-Routen per lokaler Session / Token
- serverseitige Trennung zwischen `viewer`, `operator` und `admin`
- Admin-only Benutzerverwaltung
- abgesicherte kritische Schreibpfade fuer Assets, Inventory, Labels, Fotos, Tasks, Alerts, Regeln und weitere operative Module
- vorbereitete Erweiterbarkeit fuer spaetere feinere Berechtigungen

## Bewusst noch nicht enthalten

- OAuth / OIDC / SSO
- LDAP
- 2FA
- Passwort-Reset per Mail
- Multi-Tenant- oder Teammodell
- feingranulare Objektrechte
- vollstaendiges Audit-Log-System

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

---

## Priorität B – ReactorOps Ausbau

5. ReactorOps / Digital Twin V1
6. Reactor Control / Telemetry V1
7. Calibration / Maintenance / Safety V1

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
- Scheduler
- Manual Override
- Modul-/Node-Struktur
- ACK-/Command-Vorbereitung
- Export / API

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
