
Experiment-Template + Laborjournal-Vorlage für Obsidian“

  

Perfekt — das ist der Schritt, der dein ganzes Setup „professionell“ macht.  
Ich gebe dir eine **komplette, direkt nutzbare Obsidian-Vorlage + Struktur**, inkl.:

- Experiment-Template
    
- Laborjournal (täglich)
    
- Chargen-Tracking
    
- Auswertung
    
- SOP-Integration
    

👉 Copy & Paste ready.

---

# 📁 Empfohlene Ordnerstruktur (Obsidian)

/Lab  
  /Experimente  
  /Chargen  
  /Journal  
  /SOP  
  /Referenzen  
  /Templates

---

# 📄 TEMPLATE 1 – Experiment

---  
id: EXP-{{date:YYYYMMDD}}-{{time:HHmm}}  
title: ""  
status: geplant  
typ: experiment  
prioritaet: normal  
  
ziel: ""  
hypothese: ""  
  
kultur: ""  
medium: ""  
reaktor: ""  
  
start_datum: {{date:YYYY-MM-DD}}  
end_datum:  
  
variablen:  
  hauptvariable: ""  
  konstanten: []  
  
setup:  
  temperatur: ""  
  licht: ""  
  luft: ""  
  volumen: ""  
  inokulum: ""  
  
messplan:  
  - parameter: OD680  
    intervall: ""  
  - parameter: OD780  
    intervall: ""  
  - parameter: pH  
    intervall: ""  
  - parameter: temperatur  
    intervall: ""  
  
erfolgskriterien:  
  - ""  
abbruchkriterien:  
  - ""  
  
verknuepfte_chargen: []  
verknuepfte_journal_eintraege: []  
  
notizen: ""  
---  
  
# Experiment {{title}}  
  
## Ziel  
{{ziel}}  
  
## Hypothese  
{{hypothese}}  
  
## Setup  
- Kultur: {{kultur}}  
- Medium: {{medium}}  
- Reaktor: {{reaktor}}  
  
## Variablen  
- Hauptvariable: {{variablen.hauptvariable}}  
- Konstanten: {{variablen.konstanten}}  
  
## Ablauf  
1. Vorbereitung  
2. Start  
3. Messungen  
4. Auswertung  
  
## Messdaten (Roh)  
  
| Zeit | OD680 | OD780 | pH | Temp | Notizen |  
|------|------|------|-----|------|--------|  
  
## Beobachtungen  
  
## Ergebnis  
  
## Bewertung  
- [ ] erfolgreich  
- [ ] teilweise  
- [ ] fehlgeschlagen  
  
## Learnings  
  
## Nächste Schritte

---

# 📄 TEMPLATE 2 – Laborjournal (täglich)

---  
date: {{date:YYYY-MM-DD}}  
typ: journal  
  
aktive_experimente: []  
aktive_chargen: []  
  
raumzustand: sauber  
clean_bench: ok  
besonderheiten: ""  
  
---  
  
# Laborjournal {{date}}  
  
## Allgemeiner Zustand  
- Raum:   
- Clean Bench:   
- Luftsystem:   
- Inkubator:   
- Reaktoren:   
  
## Messungen  
  
### Reaktor 1  
- OD680:  
- OD780:  
- pH:  
- Temp:  
- visuell:  
  
### Reaktor 2  
- OD680:  
- OD780:  
- pH:  
- Temp:  
- visuell:  
  
---  
  
## Mikroskopie  
- Beobachtungen:  
- Auffälligkeiten:  
  
---  
  
## Agar Tests  
- durchgeführt: ja / nein  
- Ergebnis:  
  
---  
  
## Probleme / Auffälligkeiten  
  
---  
  
## Maßnahmen  
  
---  
  
## Fotos / Referenzen  
  
---  
  
## Bewertung des Tages  
- [ ] stabil  
- [ ] beobachten  
- [ ] kritisch

---

# 📄 TEMPLATE 3 – Charge (Kultur-Tracking)

---  
id: CHG-{{date:YYYYMMDD}}-{{time:HHmm}}  
typ: charge  
  
kultur: ""  
stamm: ""  
quelle: ""  
  
medium: ""  
wasserquelle: ""  
  
reaktor: ""  
  
start: {{date:YYYY-MM-DD}}  
status: aktiv  
  
sensor_status:  
  kalibriert: nein  
  
verknuepfte_experimente: []  
verknuepfte_journal_eintraege: []  
  
---  
  
# Charge {{id}}  
  
## Herkunft  
- Kultur:  
- Stamm:  
- Quelle:  
  
## Setup  
- Medium:  
- Wasser:  
- Reaktor:  
  
## Verlauf  
  
| Datum | OD680 | pH | Temp | Zustand |  
|------|------|----|------|--------|  
  
## Beobachtungen  
  
## Probleme  
  
## Maßnahmen  
  
## Bewertung  
  
- [ ] sauber  
- [ ] verdächtig  
- [ ] kontaminiert  
  
## Ergebnis  
  
- [ ] erfolgreich  
- [ ] verworfen

---

# 📄 TEMPLATE 4 – Auswertung

---  
typ: auswertung  
experiment: ""  
datum: {{date:YYYY-MM-DD}}  
---  
  
# Auswertung {{experiment}}  
  
## Zusammenfassung  
  
## Datenanalyse  
  
## Trends  
  
## Auffälligkeiten  
  
## Vergleich mit Hypothese  
  
## Fazit  
  
## Optimierung  
  
## Nächste Experimente

---

# 📄 TEMPLATE 5 – SOP Referenz

---  
typ: sop  
bereich: ""  
version: 1.0  
---  
  
# SOP: {{bereich}}  
  
## Zweck  
  
## Materialien  
  
## Ablauf  
  
## Kritische Punkte  
  
## Fehlerquellen  
  
## Kontrolle

---

# 🔗 Verknüpfungslogik (WICHTIG)

Nutze in Obsidian:

- [[EXP-...]]
    
- [[CHG-...]]
    
- [[2026-04-16]]
    

👉 alles verlinken!

---

## Beispiel

Im Experiment:

verknuepfte_chargen:  
- [[CHG-20260416-1030]]

---

# 🧠 Workflow (wie du es wirklich nutzt)

---

## Schritt 1 – Experiment erstellen

→ Template 1

---

## Schritt 2 – Charge anlegen

→ Template 3

---

## Schritt 3 – täglich Journal

→ Template 2

---

## Schritt 4 – alles verlinken

---

## Schritt 5 – am Ende Auswertung

→ Template 4

---

# 📊 Bonus: Status-System

Nutze Status-Felder:

- geplant
    
- aktiv
    
- abgeschlossen
    
- abgebrochen
    

---

# 🧠 Best Practices

- lieber zu viel dokumentieren als zu wenig
    
- immer gleiche Struktur nutzen
    
- Fotos machen!
    
- keine „Gedächtnis-Dokumentation“
    
- täglich kurz eintragen statt selten viel
    

---

# 🚀 Optional (sehr stark)

Wenn du willst, kannst du später:

- Obsidian + MQTT verbinden
    
- automatische Messdaten einfügen
    
- Dashboard bauen
    

---

# 🧠 Fazit

Mit diesem Setup hast du:

👉 echtes Laborjournal-System  
👉 nachvollziehbare Experimente  
👉 reproduzierbare Prozesse  
👉 Basis für Automatisierung + AI

---

# 👉 Nächster sinnvoller Schritt

Jetzt kannst du:

### Option A

👉 **Dataview Dashboard (Übersicht aller Experimente + Chargen)**

### Option B

👉 **MQTT → Obsidian Integration (automatische Daten)**

### Option C

👉 **ABrain + Lab = automatische Analyse**

---

Ich würde dir empfehlen:

👉 **Dataview Dashboard als nächstes**

  

Freigabe-Workflow als Markdown-Handbuch.

  

Alles klar — jetzt bauen wir den **entscheidenden Teil deines Systems**:

👉 einen **klaren, professionellen Freigabe-Workflow**, der festlegt:  
**Wann ist eine Charge „ok“, „unsicher“ oder „nicht essbar“?**

Das ist bewusst konservativ aufgebaut — wie im echten Labor:  
👉 lieber eine Charge verwerfen als ein Risiko eingehen.
