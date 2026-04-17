
# 📄 DIY Mikroalgen-Labor – Systemhandbuch v1

---

# 1. SYSTEMÜBERSICHT

## Ziel

Aufbau eines **reproduzierbaren, sauberen, datengetriebenen Mikroalgen-Labors** mit:

- kontrollierter Kultivierung
    
- quantitativer Messung
    
- Kontaminationskontrolle
    
- klaren Freigabeprozessen
    

---

## Architektur

[ Clean Zone / Agar / Inokulation ]  
                ↓  
         [ Inkubator ]  
                ↓  
          [ Shaker ]  
                ↓  
     [ Photobioreaktoren ]  
                ↓  
   [ Sensorik + Gas + Licht ]  
                ↓  
     [ Spectrophotometer ]  
                ↓  
      [ Zentrifuge / Ernte ]  
                ↓  
        [ Analyse / Freigabe ]

---

# 2. DIY SPECTROPHOTOMETER (OD SYSTEM)

## Ziel

Messung von:

- Biomasse (OD)
    
- Wachstum
    
- Stress / Kontamination
    

---

## Hardware

### Komponenten

- LED 680 nm (Chlorophyll)
    
- LED 780 nm (Trübung)
    
- Photodiode
    
- OpAmp (Transimpedanz)
    
- ADC (ADS1115)
    
- Raspberry Pi Zero
    
- Küvette (10 mm)
    
- 3D-gedrucktes Gehäuse (lichtdicht)
    

---

## Aufbau

LED → Probe → Photodiode

- Abstand fix
    
- schwarzes Gehäuse
    
- keine Streulicht-Leaks
    

---

## Kalibrierung

1. Dunkelwert messen
    
2. Leerprobe (Medium)
    
3. Verdünnungsreihe
    

---

## Output

- OD680
    
- OD780
    
- Ratio OD680/OD780
    

---

## Nutzung

- Wachstumskurve
    
- Vergleich von Kulturen
    
- Frühwarnsystem
    

---

# 3. STERILE LUFTSTATION

## Ziel

Vermeidung von Kontamination über Luft

---

## Aufbau

Pumpe  
 → Vorfilter  
 → Aktivkohle (optional)  
 → Verteiler  
 → pro Reaktor:  
      0.2 µm hydrophober Filter  
      Rückschlagventil  
      → Reaktor

---

## Komponenten

- Membranpumpe
    
- Inline-Filter (0.2 µm)
    
- Silikonschläuche
    
- Verteilerblock (3D Druck möglich)
    
- Rückschlagventile
    
- Luftstein / Diffusor
    

---

## Regeln

- jeder Reaktor eigener Endfilter
    
- Filter regelmäßig tauschen
    
- kein Rückfluss
    

---

# 4. AGAR SETUP

## Ziel

Screening auf Kontamination

---

## Ausstattung

- Petrischalen
    
- Agar (TSA / PDA)
    
- Pipetten
    
- Inokulationsschleife
    
- Inkubator
    

---

## Tests

### Routine

- Luftplatten (offen 10–20 min)
    
- Abklatschproben
    
- Wasserprobe
    
- Reaktorprobe
    

---

## Bewertung

- Wachstum = Hinweis, nicht Beweis
    
- Trends beobachten
    

---

# 5. SENSORIK

## Pflicht

- Temperatur
    
- pH
    
- Leitfähigkeit
    
- OD (Spectro)
    

---

## Erweiterung

- DO (Sauerstoff)
    
- Licht
    
- Luftstrom
    

---

## Struktur

Sensor → Pi Zero → MQTT → DB

---

# 6. LICHTSYSTEM

## Setup

- LED Panels / Strips
    
- definierter Abstand
    
- gleiche Geometrie
    

---

## Steuerung

- Timer
    
- optional PWM
    

---

## Dokumentation

- Lichtdauer
    
- Intensität
    
- Position
    

---

# 7. DATENLOGGING

## Stack

- MQTT Broker
    
- InfluxDB / SQLite
    
- Grafana
    

---

## Datenpunkte

- Temp
    
- pH
    
- EC
    
- OD
    
- DO
    
- Licht
    
- Luftfluss
    

---

## Regeln

- jede Messung timestamped
    
- keine „manuellen“ Daten ohne Markierung
    

---

# 8. AUTOMATISIERUNG

## Beispiele

- pH Regelung via CO₂
    
- Dosierpumpen für Nährstoffe
    
- Alarm bei:
    
    - Temp Drift
        
    - OD Drop
        
    - Luftausfall
        

---

## Logik

IF Wert außerhalb → Alert / Aktion

---

# 9. QUALITÄTSSYSTEM

## Chargenmodell

Jede Kultur = Charge

---

## Dokumentation

- Stamm
    
- Medium
    
- Wasserquelle
    
- Datum
    
- Reaktor
    
- Sensorstatus
    

---

## SOPs

- Reinigung
    
- Inokulation
    
- Messung
    
- Ernte
    

---

# 10. TESTSTRATEGIE

---

## Stufe 1 – intern

- Mikroskop
    
- OD
    
- Sensoren
    
- Agar
    

👉 entscheidet: weiter / stoppen

---

## Stufe 2 – Screening

- Schnelltests (z. B. Mikrozytine)
    
- Wasserqualität
    

---

## Stufe 3 – externe Analyse

- Schwermetalle (ICP-MS)
    
- Mikrobiologie
    
- ggf. Toxine
    

---

# 11. ENTSCHEIDUNGSLOGIK

## Charge OK (intern)

- stabile OD
    
- kein Auffälliges Mikroskop
    
- Agar unauffällig
    
- Sensorwerte stabil
    

---

## Charge UNSICHER

- leichte Abweichung  
    → Beobachten / isolieren
    

---

## Charge FAIL

- Geruch / Farbe falsch
    
- Agar stark
    
- OD unstabil
    

→ **verwerfen**

---

# 12. SICHERHEIT

## Grundregeln

- nichts essen ohne externe Prüfung
    
- sauberes Wasser verwenden
    
- keine unbekannten Arten
    
- keine „Rettungsversuche“ bei Kontamination
    

---

# 13. ROADMAP

## Phase 1

- Spirulina stabilisieren
    
- Spectro bauen
    

## Phase 2

- Agar Routine
    
- Datenlogging
    

## Phase 3

- Automatisierung
    
- mehrere Kulturen
    

## Phase 4

- externe Tests
    
- Qualitätssystem
    

---
