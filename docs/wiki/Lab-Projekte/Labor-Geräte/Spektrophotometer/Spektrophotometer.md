
# 📄 DIY Spectrophotometer v1 (OD680 / OD780)

## 🧭 Ziel

Messung von:

- Biomasse (OD)
    
- Wachstumskurven
    
- Stress / Kontamination
    
- Vergleich von Kulturen
    

👉 ausgelegt für:

- Spirulina
    
- Chlorella
    
- Nannochloropsis
    

---

# 🧱 1. Systemprinzip

LED → Probe (Küvette) → Photodiode → ADC → Raspberry Pi

---

# ⚙️ 2. Komponenten (konkret)

## 🔷 Optik

- LED 680 nm (Pflicht)
    
- LED 780 nm (sehr empfohlen)
    
- Photodiode (z. B. BPW34)
    

---

## 🔷 Elektronik

- OpAmp (z. B. MCP6002 / TLV2372)
    
- Widerstände (10k–1M je nach Gain)
    
- ADS1115 (I2C ADC)
    
- Raspberry Pi Zero
    

---

## 🔷 Mechanik

- Küvette (10 mm Standard)
    
- 3D gedrucktes Gehäuse (lichtdicht!)
    
- Küvettenhalter
    

---

## 🔷 Sonst

- schwarze Farbe / Tape innen
    
- stabile Halterung
    

---

# 🧱 3. Mechanischer Aufbau

## Gehäuse (wichtig!)

- komplett lichtdicht
    
- innen schwarz matt
    
- LED und Sensor exakt gegenüber
    

[LED] → | Küvette | → [Photodiode]

---

## Abstand

- konstant halten (~20–30 mm gesamt)
    
- keine Bewegung
    

---

## Fehler vermeiden

❌ Streulicht  
❌ schief eingesetzte Küvette  
❌ glänzende Innenflächen

---

# 🔌 4. Elektronik (einfach & stabil)

## Photodiode-Schaltung

Photodiode → OpAmp (Transimpedanz)  
           → ADC (ADS1115)

---

## Prinzip

- Licht → Strom
    
- OpAmp → Spannung
    
- ADC → digital
    

---

## Gain einstellen

- dunkle Probe → niedriger Gain
    
- helle Probe → höherer Gain
    

👉 Start:

- 100k–470k Feedback Widerstand
    

---

# 🧠 5. Messstrategie

## Wellenlängen

- **680 nm → Chlorophyll**
    
- **780 nm → Trübung**
    

---

## Output

- OD680
    
- OD780
    
- Ratio = OD680 / OD780
    

---

# 💻 6. Software (Python, Raspberry Pi)

## Installation

sudo apt update  
sudo apt install python3-pip  
pip install adafruit-circuitpython-ads1x15

---

## Python Code

import time  
import board  
import busio  
import adafruit_ads1x15.ads1115 as ADS  
from adafruit_ads1x15.analog_in import AnalogIn  
  
# I2C Setup  
i2c = busio.I2C(board.SCL, board.SDA)  
ads = ADS.ADS1115(i2c)  
  
# Channels  
chan_680 = AnalogIn(ads, ADS.P0)  
chan_780 = AnalogIn(ads, ADS.P1)  
  
# Calibration values (set later)  
I0_680 = 1.0  
I0_780 = 1.0  
  
def calculate_od(I, I0):  
    if I <= 0:  
        return 0  
    import math  
    return -math.log10(I / I0)  
  
while True:  
    I_680 = chan_680.voltage  
    I_780 = chan_780.voltage  
  
    od_680 = calculate_od(I_680, I0_680)  
    od_780 = calculate_od(I_780, I0_780)  
  
    ratio = od_680 / od_780 if od_780 != 0 else 0  
  
    print(f"OD680: {od_680:.3f} | OD780: {od_780:.3f} | Ratio: {ratio:.3f}")  
  
    time.sleep(2)

---

# 🧪 7. Kalibrierung (KRITISCH!)

## Schritt 1: Dunkelwert

- LED aus
    
- messen → Offset speichern
    

---

## Schritt 2: Leerprobe (Medium)

- Küvette mit Medium
    
- I0 speichern
    

I0_680 = gemessener Wert  
I0_780 = gemessener Wert

---

## Schritt 3: Verdünnungsreihe

z. B.:

- 100%
    
- 50%
    
- 25%
    
- 12.5%
    

👉 plotten → lineare Kurve prüfen

---

# 📊 8. Interpretation

## Normal

- OD steigt → Wachstum
    

## Problem

- OD fällt → Kultur stirbt
    
- OD680 ↓ aber OD780 gleich → Pigmentverlust
    
- Ratio verändert sich → Stress / Kontamination
    

---

# 📡 9. Integration in dein System

## MQTT Beispiel

import paho.mqtt.publish as publish  
  
publish.single("lab/od680", od_680, hostname="localhost")

---

## Datenbank

- InfluxDB oder SQLite
    

---

## Visualisierung

- Grafana
    

---

# ⚠️ 10. Grenzen (ehrlich)

❌ kein echtes Spektralphotometer  
❌ keine exakte Konzentration ohne Kalibrierung  
❌ empfindlich gegenüber Lichtfehlern

👉 aber:

✅ sehr gut für Trends  
✅ sehr gut für Prozesskontrolle  
✅ extrem hoher Nutzen im DIY-Lab

---

# 🚀 11. Upgrade-Pfade

## v2

- mehr Wellenlängen
    
- automatischer LED-Wechsel
    
- Flow-Cell (inline Messung)
    

---

## v3

- Kalibrierkurven speichern
    
- AI-Auswertung (ABrain)
    
- automatische Alerts
    

---

# 🧠 Fazit

Dieses System bringt dir:

👉 **Quantifizierung statt Bauchgefühl**  
👉 **frühe Fehlererkennung**  
👉 **vergleichbare Experimente**
