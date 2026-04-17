
# Experiment-Design: 10 erste Tests mit dem gesamten Setup

## Ziel dieser Testserie

Mit diesen 10 Tests sollst du am Ende beantworten können:

- Ist mein Setup dicht, stabil und reproduzierbar?
    
- Funktioniert meine sterile Arbeitsweise?
    
- Sind Sensoren und Messwerte plausibel?
    
- Kann ich Wachstum sauber erkennen?
    
- Welche Parameter haben den größten Einfluss?
    
- Wo entstehen Kontaminationen oder Prozessfehler?
    
- Welche Kulturbedingungen sind für meinen ersten stabilen Betrieb am besten?
    

---

# Grundregeln für alle 10 Tests

Für **jeden** Test solltest du immer dokumentieren:

- Test-ID
    
- Datum
    
- Ziel
    
- Kulturart
    
- Reaktor / Gefäß
    
- Medium
    
- Inokulum
    
- Temperatur
    
- Lichtdauer
    
- Lichtintensität
    
- Belüftung
    
- pH Start / Ende
    
- OD Start / Ende
    
- Beobachtungen
    
- Foto(s)
    
- Ergebnis
    
- Bewertung: erfolgreich / unklar / fehlgeschlagen
    

Wichtig:  
**Immer nur 1 Hauptvariable pro Test verändern**, sonst weißt du am Ende nicht, was den Effekt verursacht hat.

---

# Test 1 – Leerlauf / Systemvalidierung ohne Kultur

## Ziel

Prüfen, ob dein technisches System stabil läuft, bevor du lebende Kultur riskierst.

## Aufbau

- Reaktor mit sterilem oder sauberem Wasser / Medium ohne Algen
    
- Luftsystem aktiv
    
- Licht aktiv
    
- Sensorik aktiv
    
- Logging aktiv
    
- Laufzeit: 24–48 h
    

## Prüfpunkte

- Temperatur stabil?
    
- Leckagen?
    
- Kondenswasserproblem?
    
- Luftstrom konstant?
    
- ungewöhnlicher Schaum?
    
- Sensoren plausibel?
    
- Drift im pH / Leitfähigkeit?
    

## Erfolgskriterium

- kein Leck
    
- keine mechanischen Probleme
    
- keine starke Sensorabweichung
    
- Logging vollständig
    

## Nutzen

Das ist dein technischer Baseline-Test.

---

# Test 2 – Sterilitäts- und Workflow-Test

## Ziel

Prüfen, ob dein Clean-Bench-/Agar-/Handling-Workflow sauber genug ist.

## Aufbau

Führe parallel aus:

- 1 Negativkontrolle: sterile Platte ungeöffnet
    
- 1 Luftplatte im Arbeitsraum
    
- 1 Luftplatte in/an der Clean Bench
    
- 1 Oberflächenprobe von Werkbank
    
- 1 Handschuhprobe
    
- 1 Port-/Schlauchprobe
    

## Inkubation

- 25–30 °C
    
- 48–72 h
    

## Prüfpunkte

- Wo wächst etwas?
    
- Wie stark?
    
- Unterschiede zwischen Bench und Raum?
    

## Erfolgskriterium

- Clean-Bench-Proben deutlich sauberer als Raum
    
- Handschuhe/Ports nicht stark belastet
    

## Nutzen

Hier findest du deine größten Kontaminationsquellen.

---

# Test 3 – Sensorvalidierung und Kalibrier-Check

## Ziel

Prüfen, ob deine Messkette belastbar ist.

## Aufbau

Teste einzeln:

- Temperatur gegen Referenzthermometer
    
- pH gegen Pufferlösungen
    
- EC/Leitfähigkeit gegen Standard
    
- OD-Spektrophotometer mit Leerprobe + Verdünnungsreihe
    

## Prüfpunkte

- Wiederholgenauigkeit
    
- Drift
    
- lineare oder zumindest monotone Reaktion
    

## Erfolgskriterium

- mehrere Messungen liefern ähnliche Werte
    
- keine groben Ausreißer
    
- OD reagiert sauber auf Verdünnung
    

## Nutzen

Ohne diesen Test kannst du spätere biologische Ergebnisse nicht sauber interpretieren.

---

# Test 4 – OD-Korrelation mit echter Kultur

## Ziel

Prüfen, ob dein DIY-Spektrophotometer für deine Algenkultur praktisch nutzbar ist.

## Aufbau

- Nimm eine Kultur
    
- mache eine Verdünnungsreihe, z. B. 100 %, 75 %, 50 %, 25 %, 12,5 %
    
- miss jede Stufe:
    
    - OD680
        
    - OD780
        
    - Foto
        
    - optional Mikroskopie
        

## Prüfpunkte

- steigt/fällt OD erwartbar?
    
- ist die Kurve plausibel?
    
- verhalten sich OD680 und OD780 sinnvoll?
    

## Erfolgskriterium

- Verdünnungen lassen sich klar voneinander unterscheiden
    
- keine chaotischen Messsprünge
    

## Nutzen

Ab dann wird dein OD-System ein echtes Prozesswerkzeug.

---

# Test 5 – Starterkultur-Aufbau im Shaker

## Ziel

Prüfen, ob du kleine Kulturen sauber und reproduzierbar hochfahren kannst.

## Aufbau

- 3 identische kleine Kulturen im Shaker
    
- identisches Medium
    
- identisches Startvolumen
    
- identisches Inokulum
    

## Variablen

Keine. Das ist ein Reproduzierbarkeitstest.

## Prüfpunkte

- wachsen alle ähnlich?
    
- gleiche Farbe?
    
- ähnliche OD?
    
- Agar/Mikroskop unauffällig?
    

## Erfolgskriterium

- alle 3 Ansätze entwickeln sich ähnlich
    

## Nutzen

Das ist dein erster echter Test auf Reproduzierbarkeit.

---

# Test 6 – Reaktor-Scale-up vom Shaker in den PBR

## Ziel

Prüfen, ob der Übergang vom Startersystem in den PBR sauber funktioniert.

## Aufbau

- Starterkultur aus Test 5
    
- Überführung in PBR
    
- Standardbedingungen für Spirulina oder deine Zielalge
    
- Laufzeit: mehrere Tage
    

## Prüfpunkte

- Startverhalten
    
- Anpassungsphase
    
- OD-Verlauf
    
- Farbe, Geruch, Schaumbildung
    
- Mikroskopie
    
- Agar-Screening punktuell
    

## Erfolgskriterium

- Kultur wächst an oder bleibt stabil
    
- keine starke Frühkontamination
    
- keine mechanischen Probleme
    

## Nutzen

Das ist der erste echte Prozessketten-Test.

---

# Test 7 – Licht-Test

## Ziel

Prüfen, welchen Einfluss Licht auf Wachstum und Stress hat.

## Aufbau

3 parallele Ansätze:

- niedriges Licht
    
- mittleres Licht
    
- höheres Licht
    

Alle anderen Bedingungen gleich.

## Prüfpunkte

- OD-Anstieg
    
- Farbe
    
- Klumpung
    
- Schaumbildung
    
- Temperatur durch Beleuchtung
    

## Erfolgskriterium

- du erkennst, welche Lichtstufe Wachstum fördert und welche stresst
    

## Nutzen

Licht ist bei dir eine der stärksten Stellgrößen.

---

# Test 8 – Temperatur-Test

## Ziel

Prüfen, in welchem Temperaturfenster deine erste Kultur am stabilsten läuft.

## Aufbau

3 parallele Ansätze, z. B.:

- niedrig
    
- Zieltemperatur
    
- etwas höher
    

Beispiel bei Spirulina:

- 28 °C
    
- 32 °C
    
- 35 °C
    

## Prüfpunkte

- Wachstum
    
- Stabilität
    
- Geruch
    
- Pigmentveränderung
    
- mikroskopische Auffälligkeiten
    

## Erfolgskriterium

- du findest das beste Arbeitsfenster, nicht nur das theoretische
    

## Nutzen

Wichtig für Inkubator, PBR und spätere Automatisierung.

---

# Test 9 – Belüftungs-/Gas-Test

## Ziel

Prüfen, wie stark Luftstrom und Durchmischung deinen Prozess beeinflussen.

## Aufbau

3 Ansätze mit:

- niedriger Belüftung
    
- mittlerer Belüftung
    
- höherer Belüftung
    

## Prüfpunkte

- Sedimentation?
    
- gleichmäßige Verteilung?
    
- Schaumbildung?
    
- pH-Verhalten?
    
- OD-Entwicklung?
    

## Erfolgskriterium

- du findest genug Durchmischung ohne unnötigen Stress oder Schaum
    

## Nutzen

Das ist entscheidend für Reaktordesign und spätere Standardisierung.

---

# Test 10 – Kontaminations-Stresstest / Prozessrobustheit

## Ziel

Prüfen, wie robust dein Workflow im Alltag ist.

## Aufbau

Nicht absichtlich „verseuchen“, sondern gezielt mehrere normale Chargen nacheinander fahren:

- gleiche SOP
    
- gleiche Kultur
    
- gleiche Parameter
    
- mehrere Durchläufe
    

## Prüfpunkte

- treten Kontaminationen wiederholt an derselben Stelle auf?
    
- driftet ein Sensor regelmäßig?
    
- ist ein Port oder Schlauchsystem problematisch?
    
- bleibt die Sterilroutine stabil?
    

## Erfolgskriterium

- mehrere Läufe hintereinander ohne ungeklärten Ausfall
    

## Nutzen

Das ist der Übergang von „es hat einmal funktioniert“ zu „ich beherrsche den Prozess“.

---

# Empfohlene Reihenfolge

Bitte nicht durcheinander starten.  
Sinnvoll ist diese Reihenfolge:

1. Leerlauf / Systemvalidierung
    
2. Sterilitäts- und Workflow-Test
    
3. Sensorvalidierung
    
4. OD-Korrelation
    
5. Starterkultur-Reproduzierbarkeit
    
6. Scale-up in PBR
    
7. Licht-Test
    
8. Temperatur-Test
    
9. Belüftungs-Test
    
10. Prozessrobustheit / Wiederholung
    

So gehst du von **Technik → Hygiene → Messung → Biologie → Optimierung**.

---

# Welche Daten du aus allen 10 Tests sammeln solltest

Am Ende dieser Serie solltest du für jede Kultur wissen:

- welches Temperaturfenster am besten funktioniert
    
- welche Lichtstärke sinnvoll ist
    
- welcher Luftstrom stabil läuft
    
- wie dein OD-Signal zu interpretieren ist
    
- welche Kontaminationsquellen auftreten
    
- welche SOP-Stellen schwach sind
    
- wie reproduzierbar dein Setup bereits ist
    

---

# Ampellogik für die Auswertung

## Grün

- erwartbares Wachstum
    
- saubere Agar-Platten oder nur minimale Hintergrundkontamination
    
- stabile Sensorik
    
- keine Auffälligkeiten in Farbe/Geruch/Mikroskop
    

## Gelb

- Wachstum vorhanden, aber unstabil
    
- einzelne Kontaminationen
    
- leichte Sensorabweichungen
    
- Wiederholung nötig
    

## Rot

- starke Kontamination
    
- OD chaotisch
    
- Kultur kippt
    
- Geruch / Schaum / Braunfärbung
    
- technische Fehler
    

---

# Mein praktischer Rat

Für den Anfang würde ich diese 10 Tests **nur mit einer Kultur** machen, idealerweise mit deiner robustesten Kultur.

Also zuerst:

- nicht 5 Arten parallel
    
- nicht gleichzeitig zig Variablen
    
- nicht direkt „Nährstoff-Maximierung“
    

Erst wenn dein Prozess sauber läuft, lohnt sich Optimierung wirklich.