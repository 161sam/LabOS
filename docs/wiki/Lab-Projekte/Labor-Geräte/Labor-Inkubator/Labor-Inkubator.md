
# 📄 DIY Labor-Inkubator (12V Kühlbox Mod)

## 🧭 Ziel

Ein kompakter Inkubator für:

- Starterkulturen (z. B. Chlorella)
    
- Agar-Platten (optional)
    
- kleine Reaktoren / Proben
    
- kontrollierte Temperaturtests
    

👉 Zielbereich:

- **20–40 °C stabil**
    
- ±0.5–1 °C Genauigkeit (realistisch DIY)
    

---

# 🧱 1. Systemprinzip

Temperatur-Sensor → Controller → Peltier / Heizung → Innenraum  
                                   ↑  
                             Lüfter (Zirkulation)

👉 Wichtig:  
Nicht nur heizen/kühlen — **gleichmäßig verteilen**

---

# ⚙️ 2. Kühlbox verstehen (sehr wichtig)

Die meisten 12 V Kühlboxen nutzen:

- **Peltier-Element**
    
- **2 Kühlkörper + 2 Lüfter**
    
    - außen → Wärme abführen
        
    - innen → Luft bewegen
        

👉 Vorteil:

- leise
    
- kompakt  
    👉 Nachteil:
    
- ineffizient
    
- begrenzte Leistung
    

---

# 🔧 3. Umbau-Strategie (entscheidend)

Du hast 2 Optionen:

---

## 🟢 Option A – Minimal Hack (empfohlen für v1)

Du nutzt die Kühlbox fast original und ergänzt:

- Temperaturcontroller
    
- zusätzlichen Innenlüfter
    
- bessere Sensorik
    

👉 Vorteil:

- schnell
    
- zuverlässig
    

---

## 🟡 Option B – Full Control (v2)

- Peltier direkt ansteuerbar
    
- eigene H-Brücke (Heizen/Kühlen)
    
- eigene Regelung
    

👉 komplexer → später

---

# 🔌 4. Kernkomponenten

## 🔷 Temperaturcontroller

Empfehlung:

- Inkbird ITC-308 (einfach)
    
- oder DIY mit ESP32 / Raspberry Pi
    

---

## 🔷 Sensor

- DS18B20 (gut, günstig)
    
- besser: wasserdicht + kalibriert
    

👉 Position:

- NICHT an der Wand
    
- in der Luftmitte!
    

---

## 🔷 Innenlüfter (sehr wichtig!)

- 5V oder 12V PC Lüfter
    
- Dauerbetrieb
    

👉 sorgt für:

- gleichmäßige Temperatur
    
- weniger Hotspots
    

---

## 🔷 Netzteil

- 12V stabil (5–10A je nach Box)
    

---

# 🌡️ 5. Temperatur-Setup

## Zielbereiche

- Spirulina Starter: 30–35 °C
    
- Chlorella: 25–30 °C
    
- Tests: flexibel
    

---

## Controller Settings (Startwerte)

- Hysterese: 0.5–1°C
    
- Ziel: z. B. 32°C
    

---

# 🧠 6. Wichtige Modifikationen

## 🔥 1. Heizen verbessern

Viele Kühlboxen können schlecht heizen.

👉 Lösung:

- zusätzlich:
    
    - Heizmatte ODER
        
    - Keramik-Heizelement (low power)
        

---

## 🌬️ 2. Luftzirkulation

👉 Pflicht!

- kleiner Lüfter innen
    
- nicht direkt auf Proben blasen
    

---

## 💧 3. Feuchtigkeit

Optional:

- kleine Wasserschale
    

👉 verhindert:

- Austrocknung von Proben
    

---

## 🧼 4. Innenraum

- glatte Oberfläche
    
- leicht zu reinigen
    
- ggf. Kunststoffbox innen einsetzen
    

---

# 📡 7. Erweiterung (perfekt für dein System)

Du kannst den Inkubator direkt integrieren in:

- Raspberry Pi 5
    
- MQTT / n8n / ABrain
    

---

## Messwerte loggen

- Temperatur
    
- Zeit
    
- ggf. Licht (wenn integriert)
    

---

## Automation

- Alarm bei:
    
    - Temperaturabweichung
        
    - Sensorfehler
        

---

# 🧪 8. Nutzung im Algen-System

Der Inkubator ist perfekt für:

### 1. Starterkulturen

- kleine Flaschen
    
- sterile Bedingungen
    

### 2. Experimente

- Licht vs Temperatur
    
- Wachstumskurven
    

### 3. Backup-Kulturen

- extrem wichtig!
    

---

# ⚠️ 9. Typische Fehler

❌ kein Lüfter → Temperaturgradient  
❌ Sensor an Wand → falsche Werte  
❌ zu kleine Hysterese → ständiges Schalten  
❌ zu große Box → instabil  
❌ Kondensation ignorieren

---

# 🧼 10. Hygiene

- regelmäßig reinigen
    
- Alkohol (70%)
    
- keine offenen Proben lange stehen lassen
    

---

# 🚀 11. Upgrade-Pfade

## v2

- PID-Regelung
    
- dual mode (heat + cool aktiv gesteuert)
    

## v3

- mehrere Zonen
    
- Lichtintegration
    
- vollautomatisiert (ABrain)
    

---

# 🧠 Mein Engineering-Fazit

Dein Inkubator wird:

👉 **nicht der limitierende Faktor sein**  
👉 aber ein **massiver Stabilitäts-Boost** für dein System

Besonders für:

- Starterkulturen
    
- Reproduzierbarkeit
    
- Experimente
    