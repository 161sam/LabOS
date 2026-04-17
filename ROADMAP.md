# LabOS Roadmap

## Projektstatus

LabOS ist eine Raspberry-Pi-fähige Laborplattform für Planung, Protokollierung, Live-Monitoring, Chargenverwaltung, Reaktorverwaltung, Wiki/Dokumentation, Automatisierung und KI-Assistenz.

Aktueller Stand:
- Monorepo angelegt
- Frontend-Grundgerüst mit Next.js vorhanden
- FastAPI-Backend vorhanden
- Docker Compose vorhanden
- Erste Bereiche umgesetzt:
  - Dashboard
  - Chargen mit CRUD-Basis
  - Reaktoren mit CRUD-Basis
  - Sensorik V1 mit Werte-Ingest und Verlauf
  - Tasks + Alerts V1
  - Wiki
  - ABrain-Status
- Seed-Daten vorhanden
- API-Tests fuer Healthcheck, Charge-CRUD, Reactor-CRUD, Sensorik, Tasks und Alerts vorhanden
- Alembic-Basis fuer reproduzierbare Migrationen vorhanden

Ziel ist eine lokal betreibbare, modulare, skalierbare Labor-App für Raspberry Pi 4/5 und spätere Erweiterung auf Multi-Node-Setups.

---

## Leitprinzipien

1. Local first
2. Raspberry-Pi-tauglich
3. Offline-fähig
4. Modular statt monolithisch
5. Saubere APIs statt enger Kopplung
6. Dokumentation als Produktbestandteil
7. Automatisierung kontrolliert und nachvollziehbar
8. KI als Assistenz, nicht als Blackbox-Kern
9. Laborbetrieb vor Feature-Spielerei
10. Kleine, saubere, testbare Inkremente

---

## Produktvision

LabOS soll das zentrale Betriebssystem für das Projekt werden. Alles, was im Labor passiert, wird darüber:

- geplant
- dokumentiert
- überwacht
- ausgewertet
- automatisiert
- historisiert
- erklärt
- verbessert

Langfristig bildet LabOS den digitalen Zwilling des realen Laborbetriebs.

---

# Versionen und Meilensteine

## v0.1.0 – Bootstrap
Status: abgeschlossen

Inhalt:
- Repo-Struktur
- Docker Compose
- Frontend-Basis
- API-Basis
- Dashboard-Übersicht
- Chargen-Liste
- Reaktoren-Liste
- Wiki-Basis
- ABrain-Status-Endpunkt
- Seed-Daten
- Health-Test

Ergebnis:
- startfähiges Grundsystem
- lokal entwickelbar
- Basis für alle Folgearbeiten

---

## v0.1.1 – Solide CRUD-Basis
Status: umgesetzt als aktueller Entwicklungsschritt

Ziele:
- echte Create/Edit/Status-Flows fuer Chargen
- echte Create/Edit/Status-Flows fuer Reaktoren
- Formulare im Frontend
- Validierung im Backend
- Fehlerzustände sauber behandeln
- API-Antworten konsistent machen

Umfang:
- Charge anlegen
- Charge bearbeiten
- Charge archivieren / Status ändern
- Reaktor anlegen
- Reaktor bearbeiten
- Reaktor stilllegen / Status ändern
- UI-Feedback (loading, success, error)
- Detailendpunkte fuer Charge und Reaktor
- Backend-Tests fuer Create, Update, Detail und Statuswechsel

Akzeptanzkriterien:
- Chargen und Reaktoren vollständig im UI pflegbar
- Keine Seed-Abhängigkeit für sinnvolle Nutzung
- Alle Kernfelder validiert
- Fehler im UI verständlich sichtbar

Offen nach diesem Schritt:
- Delete-/Archivierungsstrategie bewusst separat halten
- Alembic als naechsten Schritt nachziehen

---

## v0.1.2 – Datenmodell und Persistenz härten
Status: umgesetzt als aktueller Entwicklungsschritt

Ziele:
- Alembic-Migrationen einführen
- DB-Struktur stabilisieren
- Basisschema erweitern
- technische Schulden aus Bootstrap abbauen

Umfang:
- Migration-Setup
- initiale Baseline-Migration fuer aktuelles Kernschema
- reproduzierbare DB-Upgrades fuer leere und bestehende Bootstrap-Datenbanken
- Indizes fuer Charge- und Reactor-Listen/Statusabfragen
- dokumentierter Workflow fuer Upgrade und neue Migrationen
- Seed-Flow sauber hinter Migrationen eingehangen

Akzeptanzkriterien:
- DB-Änderungen reproduzierbar migrierbar
- Kein Schema-Drift
- Entwicklungsumgebung zuverlässig neu aufsetzbar

Offen nach diesem Schritt:
- fachliche Constraints und Relationen mit den naechsten Modulen erweitern
- Archivierungsstrategie und spaetere Deletes bewusst separat behandeln

---

## v0.1.3 – Sensorik V1
Status: umgesetzt als aktueller Entwicklungsschritt

Ziele:
- Sensoren als erste echte Live-Datenquelle integrieren

Umfang:
- Datenmodell für Sensoren und Sensorwerte
- Ingest-Endpunkt
- Testdaten-Generator
- Sensor-Übersicht im Frontend
- Zeitreihen-Grundansicht
- Zustandsampel für Sensoren
- manuelle Werterfassung ueber UI und API
- Dashboard-Ueberblick fuer letzte Sensorwerte

Mögliche Sensoren:
- Temperatur
- Luftfeuchte
- Wassertemperatur
- pH
- EC
- Licht
- CO₂ optional

Akzeptanzkriterien:
- Sensorwerte werden gespeichert
- Sensorwerte werden im Dashboard angezeigt
- Verlauf ist pro Sensor sichtbar
- Fehlerhafte/fehlende Werte werden markiert

Offen nach diesem Schritt:
- Alerts, Aufgaben und Automationsregeln noch bewusst separat halten
- keine Live-Streams, keine Hardware-Treiber und keine Spezialdatenbank in V1

---

## v0.1.4 – Aufgaben, Planung und Alerts
Status: umgesetzt als aktueller Entwicklungsschritt

Ziele:
- operative Laborarbeit im System abbilden

Umfang:
- Tasks-Modul
- Fälligkeiten
- Zustände (open, doing, done, blocked)
- Alerts-Modul
- manuelle Alerts mit Quittierung und Aufloesung
- Dashboard-Widgets für heutige Aufgaben und kritische Alerts
- Zuordnung von Tasks zu Chargen und Reaktoren
- Seed-Daten fuer Aufgaben und Alerts
- Backend-Tests fuer Task- und Alert-Flows

Beispiele:
- Probe ziehen
- pH prüfen
- Medium wechseln
- Ernten
- Reinigung
- Sensor kalibrieren

Akzeptanzkriterien:
- Aufgaben lassen sich planen und abhaken
- Alerts erscheinen und sind im UI quittierbar bzw. aufloesbar
- Chargen und Reaktoren können Aufgaben/Alerts zugeordnet werden

Offen nach diesem Schritt:
- automatische Sensor-zu-Alert-Regeln folgen bewusst spaeter
- Benachrichtigungskanaele und Eskalationen sind noch nicht enthalten

---

## v0.1.5 – Wiki V1 integrieren
Ziele:
- LabOS als Wissens- und Betriebsplattform nutzbar machen

Umfang:
- Wiki-Index
- Markdown-Rendering
- Kategorien
- Suche
- Verknüpfung aus operativen Bereichen ins Wiki
- Bereiche:
  - How-to
  - SOP
  - FAQ
  - Dev Docs
  - User Docs
  - Biology
  - Hardware

Akzeptanzkriterien:
- Wiki-Seiten im UI lesbar
- Seiten logisch gruppiert
- Laborobjekte können auf relevante Doku verweisen

---

## v0.1.6 – Foto- und Vision-Basis
Ziele:
- visuelle Dokumentation und einfache Bildauswertung vorbereiten

Umfang:
- Foto-Upload
- Zuordnung zu Charge/Reaktor/Ereignis
- Foto-Timeline
- Storage-Konzept
- Vision-Service-Stubs
- erste Metadatenextraktion

Später anschließbar:
- Füllstandserkennung
- Farbveränderung
- Kontaminationshinweise
- Trübungsentwicklung
- Schaumerkennung

Akzeptanzkriterien:
- Fotos werden gespeichert und angezeigt
- Fotos sind Objekten zugeordnet
- Grundstruktur für Vision-Pipeline vorhanden

---

## v0.1.7 – ABrain Integration V1
Ziele:
- LabOS mit Assistenzlogik verbinden

Umfang:
- ABrain-Connector erweitern
- Kontextabfragen aus LabOS
- feste Prompts / Tools für Laborfragen
- erste Chat-/Assistenzseite
- Status- und Fehlerhandling

Beispiel-Fragen:
- Welche Charge braucht heute Aufmerksamkeit?
- Welche Reaktoren sind ohne aktuelle Werte?
- Welche Aufgaben sind überfällig?
- Welche Probleme traten in den letzten 7 Tagen gehäuft auf?

Akzeptanzkriterien:
- ABrain kann strukturierte LabOS-Daten lesen
- Antworten basieren nachvollziehbar auf Systemdaten
- Kein harter Zwang zu Cloud-Modellen

---

## v0.1.8 – Automationsregeln V1
Ziele:
- nachvollziehbare, kontrollierte Automatisierung einführen

Umfang:
- Rule-Modell
- einfache IF/THEN-Regeln
- Regel-Editor
- Event-Log
- Dry-Run-Modus
- manuelle Freigabeoption für kritische Aktionen

Beispiele:
- Wenn Temperatur > X, Alert erzeugen
- Wenn pH außerhalb Bereich, Aufgabe anlegen
- Wenn Charge Tag 10 erreicht, Probenahme erinnern

Akzeptanzkriterien:
- Regeln sind im System sichtbar
- Regelaktionen werden protokolliert
- Keine unsichtbare Automatisierung

---

## v0.1.9 – Auth, Rollen, Sicherheit
Ziele:
- Vorbereitung für Mehrnutzerbetrieb

Umfang:
- Login
- Benutzerrollen
- einfache Rechteprüfung
- sichere Konfiguration
- Secrets nicht im Repo
- Backups/Restore-Konzept
- Audit-Logs vorbereiten

Rollen anfangs:
- admin
- operator
- viewer

Akzeptanzkriterien:
- Zugriff ist absicherbar
- kritische Aktionen sind autorisierbar
- grundlegende Sicherheitsbasis vorhanden

---

## v0.2.0 – Operativ nutzbares LabOS
Zielbild:
- Chargenverwaltung nutzbar
- Reaktorverwaltung nutzbar
- Sensorik eingebunden
- Aufgaben und Alerts aktiv
- Wiki integriert
- Fotos nutzbar
- ABrain-Grundanbindung vorhanden
- erste Automationsregeln vorhanden
- auf Raspberry Pi stabil lauffähig

---

# Funktionsbereiche

## 1. Core Lab Operations
- Chargen
- Reaktoren
- Aufgaben
- Events
- Statusmodelle
- Historie

## 2. Monitoring
- Sensoren
- Sensorwerte
- Live-Anzeige
- Zeitreihen
- Zustandsbewertung
- Alerts

## 3. Knowledge
- Wiki
- SOPs
- Tutorials
- FAQ
- Dev Docs
- Verknüpfungen zu realen Objekten

## 4. Intelligence
- ABrain
- Kontextabfragen
- Auswertung
- Assistenz
- Vision-Integration

## 5. Automation
- Regeln
- Event-Handling
- Planbare Jobs
- Logging
- Nachvollziehbarkeit

## 6. Platform
- Auth
- Rollen
- Backups
- Config
- Deployment
- Tests
- Observability

---

# Technische Roadmap

## Frontend
- konsistentes Layout
- Navigation vereinheitlichen
- Form-Komponenten
- Tabellenansichten
- Detailseiten
- Charts
- Fehler-/Loading-Zustände
- mobile brauchbar
- Pi-Touchscreen-tauglich

## Backend
- CRUD konsolidieren
- Schemas härten
- Services statt Logik in Routern
- Migrationen
- Tests ausbauen
- Jobs/Worker einführen
- Sensor-Ingest
- Regel-Engine vorbereiten

## Datenbank
- Migrationsstrategie
- Indizes
- Historisierung
- Attachments/Fotos
- Ereignisprotokoll
- klare Statusfelder
- referenzielle Integrität

## Infrastruktur
- Dev/Prod-Konfiguration
- Volumes/Storage
- Backup
- Restore
- Reverse Proxy optional
- Raspberry-Pi-Deployment
- Update-Strategie

---

# Nicht-Ziele für frühe Versionen

Folgendes ist bewusst nicht Priorität für die ersten Versionen:
- komplexe Multi-Tenant-Cloud
- native Mobile App
- vollautonome Regelung ohne Kontrollmechanismen
- übertriebene Microservice-Zersplitterung
- schwere Enterprise-Features vor operativer Nutzbarkeit
- Vision/LLM als Kernersatz für saubere Datenerfassung

---

# Risiken

## Produkt-Risiken
- zu breite Vision bei zu wenig operativem Kern
- Dokumentation und Produkt driften auseinander
- Sensorik wird geplant, aber nicht real integriert
- Automatisierung wird zu früh zu komplex

## Technische Risiken
- Raspberry-Pi-Ressourcenlimit
- zu schwere Frontend-/KI-Stacks
- fehlende Datenmodell-Disziplin
- fehlende Migrationsstrategie
- UI wächst inkonsistent

## Gegenmaßnahmen
- kleine Meilensteine
- Raspberry-Pi-Testbarkeit immer mitdenken
- zuerst Kern-CRUD + Datenmodell
- AI/Vision modular anbinden
- jede größere Änderung dokumentieren

---

# Definition of Done

Ein Feature gilt als fertig, wenn:
1. Code implementiert ist
2. UI oder API sinnvoll nutzbar ist
3. Fehlerfälle berücksichtigt sind
4. Tests angemessen ergänzt wurden
5. Doku aktualisiert wurde
6. Docker/dev Setup weiter funktioniert
7. Raspberry-Pi-Tauglichkeit mitgedacht wurde

---

# Nächste konkrete Schritte

## Sofort
1. CRUD für Chargen fertig bauen
2. CRUD für Reaktoren fertig bauen
3. Alembic einführen
4. API-Struktur härten
5. Frontend-Formulare bauen

## Danach
6. Sensoren + Sensorwerte
7. Tasks + Alerts
8. Wiki-UI erweitern
9. Foto-Upload
10. ABrain mit echten LabOS-Daten koppeln

---

# Release-Logik

## Branching
- `main` = stabiler Hauptstand
- kurze Feature-Branches für zusammenhängende Arbeitspakete
- kleine Commits, klare Commit-Messages

## Releases
- `v0.1.1`
- `v0.1.2`
- ...
- `v0.1.9`
- `v0.2.0`

---

# Langfristige Perspektive

Später soll LabOS zusätzlich können:
- mehrere Laborstandorte
- mehrere Pis / Nodes
- Geräte-Autodiscovery
- Hardware-Profile
- fortgeschrittene Vision-Module
- Experiment-Design und Auswertung
- digitale SOP-Ausführung
- QR/Barcode-Workflows
- digitale Laborzwillinge
- vollständige Auditierbarkeit
- optionale Cloud-Sync
