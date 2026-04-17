
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
