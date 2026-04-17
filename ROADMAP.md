# ROADMAP

LabOS entwickelt sich zu einem modularen Operating System fuer EcoSphereLab. Der Fokus bleibt auf lokalem Betrieb, Pi-Tauglichkeit, klaren operativen Datenmodellen und kleinen nachvollziehbaren Erweiterungen.

## Produktbild

- BioOps: Charges, Reaktoren, Sensorik, Foto- und Prozessdokumentation
- MakerOps: Werkbankgeraete, Fertigungs- und Elektronik-Assets, Aufgaben und Wissensverknuepfung
- ITOps: Server, SBCs, Netzwerktechnik und spaetere Infra-Objekte
- KnowledgeOps: Wiki, SOPs, How-tos und verlinkbares Betriebswissen
- Automation: Regeln, Alerts, Tasks und nachvollziehbare Ausfuehrungen
- AI Assistenz: ABrain auf echter LabOS-Datengrundlage statt losgeloester Demo-Logik

## Bereits umgesetzt

- Charges CRUD
- Reactors CRUD
- Alembic Migrationen
- Sensorik V1
- Tasks + Alerts V1
- Photo Upload + Vision Basis V1
- ABrain Integration V1 mit echtem LabOS-Kontext
- Regelengine / Automation V1
- AssetOps / DeviceOps V1
- Dashboard-Basis
- Wiki-Basis

## AssetOps / DeviceOps V1

Der aktuelle Schritt erweitert LabOS vom Prozessfokus auf reale Geraete und Assets des gesamten Labs.

Enthalten:

- Asset-Modell fuer Geraete und langlebige Assets
- CRUD fuer Assets / Devices
- Status-, Standort- und Wartungsfelder
- optionale Wiki-Referenz
- Verknuepfungen mit Tasks und Photos ueber `asset_id`
- AssetOps-Seite in der Weboberflaeche
- Dashboard-KPIs fuer aktive Assets, Wartung, Fehler und naechste Wartungen

Bewusst noch nicht enthalten:

- Inventory / MaterialOps
- Bestands- und Beschaffungslogik
- QR- / Label-System
- ITOps-Healthchecks und Monitoring-Collector
- CMDB- oder ERP-Komplexitaet
- automatische Hardwaresteuerung

## Naechste priorisierte Schritte

1. Inventory / MaterialOps V1
2. QR / Label / Traceability V1
3. ITOps / InfraOps V1 fuer Hosts, Nodes und Netzwerkobjekte
4. Asset-nahe Wartungslogik mit Alerts und Regeln
5. Sensorik V2 mit Asset- und Device-Bezug
6. Wiki-UI V2 mit tieferen Referenzen zwischen Objekten und Dokumenten
7. Vision V2 fuer strukturierte Foto-Auswertung
8. Rollen / Auth

## Architekturleitlinien fuer die naechsten Schritte

- modularer Monolith vor Service-Aufspaltung
- lokale Datenhaltung vor Cloud-Annahmen
- wenige klare Modelle statt generischer Meta-Systeme
- Erweiterungen entlang realer Betriebsobjekte
- Cross-Domain-Verknuepfungen explizit und nachvollziehbar halten

## Wichtige Abgrenzungen

- Assets / Devices sind nicht dasselbe wie Inventory
- ABrain bleibt eine angebundene Assistenzschicht, nicht das Primaersystem
- Automatisierung muss sichtbar, protokolliert und deaktivierbar bleiben
- jede Erweiterung muss fuer Raspberry Pi 4/5 praktikabel bleiben
- charge_id/reactor_id optional wenn sauber ableitbar

Wichtig:
- keine Duplikats-Explosion erzeugen
- wenn sinnvoll kleine Schutzlogik gegen identische Wiederholungen einbauen
- aber V1 pragmatisch halten

---

## 7. Frontend

Baue neue Seite:

### /automation
oder
### /rules

Mit:
- Regelliste
- Regel anlegen
- Regel bearbeiten
- aktiv/inaktiv schalten
- dry-run / evaluate button
- Anzeige letzter Ausführungen
- Ergebnis sichtbar:
  - matched / not matched
  - action executed
  - error

UX:
- funktional
- erklärbar
- keine unnötige Design-Spielerei
- Regelkonfiguration lieber klar als hyper-generisch

---

## 8. Dashboard klein ergänzen

Wenn sinnvoll klein umsetzbar:
- Anzahl aktiver Regeln
- letzte Regelereignisse oder letzte Ausführungen

Dashboard nicht aufblasen.

---

## 9. Seed / Demo

Ergänze einige sinnvolle Demo-Regeln, z. B.:
- Temperatur zu hoch -> Alert
- pH zu niedrig -> Task
- Sensor ohne Werte 24h -> Alert
- überfällige Tasks -> Alert

Wichtig:
- Seed klein und nachvollziehbar
- keine riesige Demo-Magie

---

## 10. Tests

Ergänze sinnvolle Backend-Tests für:
- Regel anlegen
- Regel validieren
- dry-run evaluation
- echte execution
- create_alert action
- create_task action
- stale sensor case
- overdue tasks case
- execution log retrieval
- Migration darf nicht brechen

Bitte robust, aber pragmatisch.

---

## 11. Doku

Aktualisiere mindestens:
- README.md
- ROADMAP.md

Dokumentiere:
- welche Regeltypen unterstützt werden
- welche Actions unterstützt werden
- was dry_run bedeutet
- wie Regeln getestet werden
- wie die Engine bewusst begrenzt ist
- wie dieser Schritt als Grundlage für spätere Multi-Domain-Erweiterungen dient

---

# Wichtige Abgrenzung

NICHT in diesem Schritt:
- GPIO / Relais / Pumpensteuerung
- Hardware Actions
- Mail / SMS / Push Notifications
- Cron-/Scheduler-Cluster
- komplexe DSL
- Multi-Step Workflows
- autonome ABrain-Ausführung
- Vision-Regeln
- Wiki-RAG oder Wissensregeln
- Rollen/Auth
- AssetOps / InventoryOps / ITOps bereits implementieren

Nur:

eine nachvollziehbare, kontrollierte Regelengine V1 mit Task/Alert-Aktionen.

---

# Technische Leitlinien

- Pi-freundlich
- keine schweren neuen Libraries
- kleine Service-Schicht
- klare API-Struktur
- lieber wenige gute Regeltypen als halbfertige Universal-Engine
- nachvollziehbare Logs
- keine stille Automatik
- spätere Erweiterung auf weitere Domänen ermöglichen, aber in diesem Schritt nicht vorwegnehmen

---

# Arbeitsweise

1. Analyse aktueller Module und vorhandener Datenquellen/Zielobjekte.
2. Minimal sauberes Rule-Modell definieren.
3. Migration bauen.
4. Backend-Engine + API implementieren.
5. UI für Regeln und Dry-Run bauen.
6. Tests ergänzen.
7. Doku aktualisieren.

---

# Abschlussausgabe

Bitte liefern:

1. Welcher Schritt wurde umgesetzt?
2. Warum war das der richtige nächste Schritt?
3. Welche Dateien wurden geändert?
4. Was wurde konkret gebaut?
5. Welche Entscheidungen wurden getroffen?
6. Welche offenen Punkte bleiben?
7. Exakte lokale Test-/Start-/Migrationsbefehle
8. Passender Commit-Message-Vorschlag

Falls sinnvoll kleine Konsistenzverbesserungen im Scope durchführen.
