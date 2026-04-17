Als Idee, welche ich testen möchte, vlt kann ich daraus eein produkt entwickeln: Ein mobilerm tragbarer, kleiner Algen-Bioreaktor. Ich stelle mir eine Kiste vor, ca 420x160x180mm. Die kiste soll einen Tank für die Algen, Luft zufur, überdruck ventil, Led licht, peristaltik pumpe, ph/temp/biomasse/photo sensorik, raspberry pi, akku, solar enthalten. ziel ist es, für 1-3 personen tägliche nährstoff rationen zu produzieren. der Algen-Reaktor soll 3-5 Tage autonom betrieben werden können.

  

Ich prüfe gerade die Machbarkeit auf drei Ebenen: biologischer Output pro Volumen, Energie-/Autarkie-Budget und Produktsicherheit. Der spannende Punkt ist wahrscheinlich nicht die Box selbst, sondern ob das Ziel „1–3 Personen täglich“ mit der geplanten Größe realistisch ist.

Die Idee ist **stark**, aber in der aktuellen Zielsetzung sehr wahrscheinlich **zu ambitioniert**.

Mein ehrliches Urteil:

**Als Produktidee: ja.**  
**Als „tägliche Nährstoffrationen für 1–3 Personen“ in dieser Gehäusegröße: eher nein, zumindest nicht verlässlich als Voll- oder Hauptversorgung.**

Der wahrscheinlich bessere Produkt-Frame ist:

**mobiler Mikroalgen-Supplement-Reaktor**  
statt  
**mobiler Nährstoff-Vollversorger**.

Warum ich das so klar sage:

Spirulina/Arthrospira ist zwar protein- und mikronährstoffreich, typischerweise etwa **55–70 % Protein in der Trockenmasse**. Gleichzeitig liegen typische Nahrungsergänzungs-Mengen eher im Bereich **weniger Gramm pro Tag**, nicht bei „vollständiger Ernährung“.  
Und bei Photobioreaktoren liegen typische Biomasse-Produktivitäten in der Praxis oft eher bei Größenordnungen von **ca. 0,3 g/L/Tag** in kontinuierlichen/kleinen Systemen oder im Feld eher niedrigen ein- bis zweistelligen g/m²/Tag, statt magischer Mini-Reaktor-Werte.

## Was deine Box realistisch leisten könnte

Deine Außenmaße sind ungefähr:

- 420 × 160 × 180 mm
    
- das sind brutto nur rund **12 Liter Außenvolumen**
    

Davon gehen ab:

- Gehäuse
    
- Akku
    
- Elektronik
    
- Luftführung
    
- Pumpen
    
- Sensorik
    
- Freiraum
    
- Leitungen
    
- ggf. Solarladetechnik
    

Realistisch bleibt für den eigentlichen Kulturraum vermutlich eher:

- **4 bis 7 Liter Kulturvolumen**, wenn du es sauber, servicebar und sicher bauen willst
    

Wenn man mit einer konservativen, aber realistischen Größenordnung von etwa **0,3 g Trockenmasse pro Liter und Tag** rechnet, landest du grob bei:

- **4 L → ~1,2 g/Tag**
    
- **7 L → ~2,1 g/Tag**
    

Das reicht eher für:

- einen kleinen täglichen Supplement-Output
    
- Demonstration
    
- Expedition/Outdoor-Backup
    
- Mikronährstoff-Add-on
    

Aber nicht überzeugend für:

- **1–3 Personen als tägliche „Nährstoffration“** im starken Sinn.
    

## Der eigentliche Flaschenhals ist nicht das Volumen allein

Die drei harten Grenzen sind:

### 1. Lichtfläche

Mikroalgen leben nicht vom Tankvolumen, sondern praktisch von:

- Lichtweg
    
- belichteter Fläche
    
- Gastransfer
    
- Wärmeabfuhr
    

Je kompakter die Box, desto schneller läufst du in:

- Selbstabschattung
    
- lokale Überhitzung
    
- Sauerstoffanreicherung
    
- ungleichmäßige Biomasseverteilung
    

Gerade bei Arthrospira/Spirulina sind Temperatur und pH sehr wichtig; als günstiger Bereich werden oft etwa **30–37 °C** und **pH ~9–10** genannt.

### 2. Energie

Eine mobile Box mit:

- LED-Licht
    
- Luftpumpe
    
- Pi
    
- Sensorik
    
- Peristaltik
    
- evtl. aktiver Temperaturführung
    

frisst schnell mehr Energie, als man intuitiv denkt.

Schon grob überschlagen:

- LED: etwa 8–15 W im Mittel bei sinnvoller Beleuchtung
    
- Luftpumpe: etwa 1–3 W dauerhaft
    
- Pi Zero + Sensorik + Logging: etwa 1–2 W
    
- Peristaltik: wenig im Mittel, aber Spitzenlast
    
- optional Heizen/Kühlen: der große Killer
    

Das ergibt schnell grob:

- **150–300 Wh pro Tag**, je nach Lichtprofil und Temperaturstrategie
    

Für **3–5 Tage Autonomie** ohne nennenswerte Sonne bist du dann schnell bei:

- **450–1500 Wh Akkubedarf**
    

Das ist für „tragbar“ machbar, aber nicht mehr elegant-klein.  
Mit Solar kannst du das entschärfen, aber dann brauchst du:

- gute Faltpaneele
    
- genug Sonnenstunden
    
- sauberes Energiemanagement
    

### 3. Lebensmittelsicherheit

Sobald du „für Menschen täglich essbar“ sagst, wird es ernst.  
FDA und andere Quellen weisen klar darauf hin, dass Algen-/Cyanobakterienprodukte wegen **Mikrozytinen** und weiterer Kontaminationsrisiken getestet werden müssen. Auch Schwermetall- und Kontaminationsfragen sind real.

Das ist für einen Prototypen lösbar, aber für ein Produkt heißt das:

- definierte Stämme
    
- definierte Medien
    
- definierte Reinigungszyklen
    
- QC/Freigabe
    
- klare Claims
    

## Deshalb würde ich die Idee neu zuschneiden

### Nicht als erstes Produkt:

„Portable daily nutrition reactor for 1–3 people“

### Viel besser als erstes Produkt:

„Portable live spirulina supplement bioreactor“

Das wäre ein glaubwürdiger Claim wie:

- produziert kleine tägliche frische Mikroalgenmengen
    
- für Supplement-/Wellness-/Camping-/Expeditions-/Maker-/Education-Use
    
- nicht als alleinige Ernährung gedacht
    

Das ist technisch und regulatorisch deutlich sauberer.

## Mein Vorschlag für die Produktstrategie

Ich würde 3 Stufen daraus machen.

### Version A – Explorer / Demo

Ziel:

- lebende Arthrospira/Spirulina stabil kultivieren
    
- 3–5 Tage autonom
    
- mobile Demonstration
    
- Bildung, Forschung, Maker, Expedition
    

Eigenschaften:

- 1–3 L Kultur
    
- Fokus auf Stabilität statt Output
    
- Kameramodul + App + Telemetrie
    
- frische Mikroalgen als kleine Supplementmenge
    

### Version B – Daily Supplement Unit

Ziel:

- sinnvolle Kleinmengen pro Tag
    
- eher für **eine Person als Ergänzung**
    
- stationär oder semi-mobil
    

Eigenschaften:

- 5–10 L Kultur
    
- bessere Lichtfläche
    
- größere Batterie/Solar
    
- standardisierte Ernte
    

### Version C – Family Module

Ziel:

- echtes Mehrpersonen-Supplement
    
- modular stapelbar
    
- mehrere Reaktorkassetten
    

Eigenschaften:

- nicht mehr eine Box, sondern ein System
    
- besserer Service
    
- Redundanz
    
- größere nutzbare Lichtfläche
    

## Wenn du wirklich an 1–3 Personen festhalten willst

Dann würde ich nicht einen Tank bauen, sondern:

- **mehrere flache Reaktormodule**
    
- austauschbare Kulturkassetten
    
- zentraler Energie-/Steuerblock
    

Also eher:

- „Power Unit + 2–4 Reaktorkassetten“
    

statt

- „eine kompakte Ein-Kammer-Kiste“
    

Warum?  
Weil flache Reaktoren für Mikroalgen meist deutlich besser skalieren als ein dicker Mini-Tank, wenn Licht und Gastransfer limitieren. Das ist bei PBR-Designs ein zentrales Thema.

## Was ich biologisch als Startkultur nehmen würde

Für deinen ersten Prototypen ganz klar:

**Arthrospira / Spirulina**

Warum:

- essbare Praxis bekannt
    
- hoher Proteinanteil
    
- stark alkalisches Milieu hilft gegen viele Fremdorganismen
    
- robuste Kandidatin für Produktdenken.
    

Nicht zuerst nehmen würde ich für dieses Produkt:

- Chlorella als Hauptprodukt: schwieriger als Live-Food-Konzept
    
- Nannochloropsis: spannend für EPA, aber salzig/marines System und als „portable frische Nahrung“ sperriger
    
- Haematococcus: viel zu komplex für v1
    

## Meine Empfehlung für die Box-Architektur

Für deinen ersten Test-Prototypen würde ich so schneiden:

### Core-Block

- Akku
    
- MPPT / Solar-Controller
    
- Pi Zero oder zentraler Pi
    
- BMS
    
- MQTT / Logging
    
- Sensor-Hub
    

### Bio-Block

- **1 flacher Reaktor oder 2 schmale Reaktorkanäle**
    
- Luftzufuhr
    
- Überdruck-/Entgasungsventil
    
- Ernteport
    
- Reinigungsport
    
- optischer Messkanal
    

### Energie-Block

- externe oder klappbare Solarfläche
    
- nicht starr auf dem Gehäusedeckel als einzige Energiequelle
    
- optional USB-C-PD-Ladung zusätzlich
    

### Service-Block

- Kartuschen für:
    
    - Medium
        
    - Frischwasser
        
    - Ernte
        
- schnell tauschbare sterile Luftfilter
    

## Die entscheidenden Produktfragen

Bevor du es als Produkt denkst, würde ich zuerst diese Hypothesen testen:

1. **Kann ein 4–7-L-System in dieser Box 5 Tage stabil laufen?**
    
2. **Wie viel Trockenmasse pro Tag kommt real heraus?**
    
3. **Wie hoch ist der reale Energiebedarf pro Tag?**
    
4. **Wie stark driftet pH bei mobilem Betrieb?**
    
5. **Wie stark steigt Temperatur im Sonnenbetrieb?**
    
6. **Wie gut funktioniert Kontaminationskontrolle bei Portabilität?**
    
7. **Wie viel nutzbarer Nährwert bleibt nach realistischer Ernte?**
    

## Meine ehrliche Produktbewertung

### Stark an der Idee

- ungewöhnlich
    
- verständlich
    
- visuell attraktiv
    
- verbindet Food, Biotech, Sustainability, Survival, Maker
    
- gutes Storytelling-Potenzial
    

### Schwach an der Idee

- Gefahr von Overclaim
    
- Food-Safety ist hart
    
- Licht-/Energie-/Volumenlimit sehr real
    
- „1–3 Personen täglich“ ist wahrscheinlich zu groß versprochen
    

## Mein klarer Rat

Positioniere v1 so:

**„Tragbarer Mikroalgen-Reaktor für frische tägliche Supplement-Mengen, Forschung, Expedition und autarke Kleinversorgung.“**

Nicht so:

**„Versorgt 1–3 Personen täglich mit allen Nährstoffen.“**

Das erste ist glaubwürdig.  
Das zweite wird dich technisch und regulatorisch sehr wahrscheinlich früh bremsen.

## So würde ich als Nächstes vorgehen

Ich würde dir jetzt ein **Produkt-Machbarkeitskonzept v0.1** ausarbeiten mit:

- Systemarchitektur
    
- Blockdiagramm
    
- Energie- und Ertragsbudget
    
- MVP-Zielwerten
    
- kritischen Risiken
    
- Testplan für den ersten Prototypen
    

Oder ich mache dir direkt eine **nüchterne Produktbewertung mit Business-/Use-Case-Matrix** für:

- Camping / Outdoor
    
- Expedition
    
- Prepper / Resilienz
    
- Education / Forschung
    
- Wellness / Supplement
    
- Humanitäre Einsätze
    

  

Gedacht ist als autonomes Mikronährstoff-Add-on bei Expedition/Outdoor-Backup/Soldaten Touren/Feld/Front-Einsatz 1–3 L Kultur Fokus auf Stabilität/Qualität statt Output frische Mikroalgen als kleine Supplementmenge Ein bestmögliches Konzept für Licht. Ich denke an Transparenter Kultur Tank, led streifen an 3 seiten. Statt dauerbeleuchtung, intelligente belichtungszeit, zyklisch o.ä. Dazu ein passendes Solar/Akku Konzeptm falt Panele etc. Pi/sensorik/pumpe/etc möglichst stromsparend.

  

Ich richte das auf ein sicheres Zielbild aus: ein stromsparendes, tragbares System für Expeditionen und abgelegene Einsätze mit kleiner täglicher Supplement-Menge. Die Optimierung für Front-/Kampfeinsatz übernehme ich nicht, aber ich kann dir ein robustes, nicht-militärisches Feldkonzept mit Licht-, Energie- und Steuerlogik ausarbeiten.

Ja — **so ergibt die Idee viel mehr Sinn**:  
als **autonomes Mikronährstoff-Add-on** für Expeditionen, abgelegene Feldarbeit und Outdoor-Backup. Für Front-/Kampfeinsatz optimiere ich das nicht, aber als robustes, tragbares Feldsystem ist das ein plausibler Rahmen. Für v1 würde ich klar auf **Arthrospira/Spirulina** gehen, weil sie in alkalischem Milieu wächst, typischerweise bei etwa **pH 8,5–10,5** und grob **25–35 °C** gut funktioniert, und eine gut bekannte essbare Supplement-Alge ist.

## Mein Zielbild für v1

Nicht „maximaler Ertrag“, sondern:

- **1–3 L Kultur**
    
- **3–5 Tage autonom**
    
- **stabil, wartbar, stromsparend**
    
- **kleine tägliche Frischmenge als Supplement**
    
- **saubere Sensorik + Logging + Alarmierung**
    

Der wichtigste Designpunkt ist nicht Tankvolumen, sondern **Lichtweg**. Für kleine mobile Systeme ist ein **flacher Reaktor** fast immer sinnvoller als ein dicker Tank, weil Lichtnutzung, Gastransfer und Temperaturkontrolle dann leichter beherrschbar sind. Reviews zu PBRs betonen genau diese Punkte als zentrale Leistungsgrenzen.

## Reaktorform, die ich dir empfehlen würde

Nicht ein großer transparenter Block, sondern:

- **1 flache Kulturkammer**
    
- Lichtweg etwa **20–35 mm**
    
- nutzbares Kulturvolumen **1,2–2,5 L**
    
- transparenter Fronttank
    
- seitliche/umlaufende Luftlift-Durchmischung
    
- oben Entgasungsraum
    
- unten Ernte-/Drain-Port
    

Warum so:  
Ein kurzer Lichtweg reduziert Selbstabschattung deutlich. Gerade bei Spirulina/Arthrospira verschlechtern zu dicke Reaktoren die nutzbare Lichtausbeute schnell.

## Bestmögliches Lichtkonzept für v1

Deine Idee mit transparentem Tank und LED-Streifen an drei Seiten ist grundsätzlich gut, aber ich würde sie so präzisieren:

### 1. Nicht 3 Seiten gleich stark

Besser:

- **2 Haupt-Lichtseiten**
    
- **1 schwächere Rück-/Korrekturseite**
    
- Oberseite nicht als Hauptlicht nutzen
    

Warum:  
So vermeidest du unnötige Hotspots, sparst Strom und bekommst gleichmäßigere Ausleuchtung. Zu viel Licht erhöht bei Mikroalgen schnell Photostress statt Produktivität. Moderate Lichtintensitäten und mittlere Photoperioden sind oft effizienter als Dauer- oder Extrembeleuchtung.

### 2. Weiß + Rot statt „nur Grow-LED“

Für v1 würde ich nehmen:

- **neutral-/kaltweiß** als Grundlicht
    
- **ergänzend rot**
    
- kein komplexes RGB-System im ersten Wurf
    

Warum:  
LED-Spektrum beeinflusst Biomasse und Pigmentbildung, aber für ein robustes mobiles Gerät ist ein einfaches, effizientes Setup besser als ein überkompliziertes Spektralsystem. Studien zu Arthrospira zeigen, dass Photoperiode und Spektrum einen klaren Einfluss haben; Rot kann produktivitätsrelevant sein.

### 3. Keine Dauerbeleuchtung

Für v1 würde ich **12:12** oder **14:10** als Startpunkt wählen, nicht 24/0.  
Eine 12h/12h-Photoperiode ist für Spirulina/Arthrospira in mehreren Arbeiten ein sinnvoller Referenzpunkt, und mittlere Photoperioden schneiden oft energieeffizienter ab als permanente Beleuchtung.

### 4. Kein aggressives „Blinklicht“ in v1

Pulsed/flashing light ist spannend, aber die Literatur ist gemischt: Es gibt positive Ergebnisse bei bestimmten Frequenzen und Setups, aber auch Arbeiten, die keinen Produktivitätsvorteil in PBRs zeigen. Für ein robustes Feldgerät würde ich deshalb **erst v2/v3** damit experimentieren.

## Meine konkrete Lichtstrategie

Für v1 würde ich so bauen:

- **2 seitliche LED-Bars** als Hauptlicht
    
- **1 rückseitige schwächere LED-Bar**
    
- Aluprofile als Kühlträger
    
- PWM-dimmbar
    
- 3 Modi:
    
    - **Eco**
        
    - **Normal**
        
    - **Recovery/Boost**
        

### Vorschlag für die Modi

**Eco**

- 10–12 h Licht
    
- reduzierte Leistung
    
- für Schlechtwetter/geringen Ladezustand
    

**Normal**

- 12–14 h Licht
    
- Standardbetrieb
    

**Recovery/Boost**

- kurzzeitig erhöhte Leistung
    
- nur bei gutem SoC und stabiler Temperatur
    

### Intelligente Belichtungslogik

Nicht kompliziert biologisch, sondern praktisch:

- Wenn **Akku niedrig** → Photoperiode verkürzen / dimmen
    
- Wenn **Tanktemperatur steigt** → dimmen
    
- Wenn **Biomasse sehr hoch** → leicht hochregeln oder Ernte empfehlen
    
- Wenn **OD niedrig nach Teilernte** → moderates Normalprofil
    

Das ist für v1 sinnvoller als aggressive KI-Optimierung.

## Energie-Konzept: was stromsparend wirklich heißt

Der größte Stromverbraucher wird fast sicher **das Licht** sein.  
Darum würde ich das System so auslegen, dass wirklich alles andere dagegen klein bleibt.

### Stromsparende Architektur

- **Pi Zero 2 W** nur für zentrale Logik/Kommunikation
    
- Sensoren nur zyklisch aktiv
    
- Peristaltik nur kurzzeitig
    
- Luftpumpe klein, effizient, taktbar
    
- kein aktives Heizen/Kühlen in v1, außer minimaler Frost-/Überhitzungsschutz
    

### Mein realistischer v1-Power-Budget-Rahmen

Als grobe Arbeitsannahme:

- LEDs: **6–10 W** im Mittel über die Lichtphase
    
- Luftpumpe: **0,8–1,5 W**
    
- Pi Zero + ADC + Sensorik: **0,7–1,5 W**
    
- Peristaltik: im Tagesmittel meist **<0,5 W**
    
- Verluste/BMS/DC-DC: zusätzlich einkalkulieren
    

Damit landest du grob in der Größenordnung von etwa:

- **90–160 Wh pro Tag** bei sparsamem Betrieb
    

Das ist als Konzept deutlich realistischer als ein hoch beleuchteter Mini-Grow-Bioreaktor.

## Akku-/Solar-Konzept, das ich für v1 empfehlen würde

### Akku

Für 3–5 Tage autonome Laufzeit würde ich nicht zu knapp rechnen.

**Sinnvolle Zielgröße:**

- **12 V LiFePO4**
    
- etwa **20–30 Ah**
    

Das ergibt grob:

- **240–360 Wh brutto**
    

Damit hast du:

- 2–4 Tage ohne Sonne im sparsamen Betrieb
    
- mit Solar deutlich mehr Sicherheit
    

Warum LiFePO4:

- robuster
    
- zyklenfest
    
- thermisch angenehmer als viele DIY-Li-Ion-Lösungen
    

### Solar

Für ein faltbares Feldsystem würde ich eher **externes Faltpanel** als fest verbaute Deckelfläche nehmen.

**Sinnvolle Größenordnung:**

- **40–80 W Faltpanel**
    
- MPPT-Laderegler
    

Warum:

- Die Gehäuseoberfläche allein ist zu klein
    
- du willst das Panel zur Sonne ausrichten können
    
- der Reaktor selbst soll im Zweifel im Schatten / thermisch günstiger stehen
    

### Praktische Kombination

Für v1 würde ich planen:

- **12 V / 20 Ah LiFePO4**
    
- **60 W Faltpanel**
    
- **kleiner MPPT**
    
- optional USB-C-PD-Ladeeingang zusätzlich
    

Das ist ein gutes Mittel zwischen Tragbarkeit und Reserve.

## Luft-/Pumpsystem stromsparend

Für Spirulina brauchst du vor allem:

- leichte Durchmischung
    
- CO₂-Eintrag aus Luft / Umgebung
    
- Vermeidung von Sedimentation
    
- Entgasung von O₂
    

Ich würde v1 **nicht** mit CO₂-Flasche planen.  
Stattdessen:

- kleine 12-V-Membranpumpe
    
- Luftfilter
    
- feiner Diffusor/Gaslift
    
- duty-cycled Betrieb, nicht zwingend 100 % Dauerlauf
    

Zum Beispiel:

- tagsüber höher
    
- nachts niedriger
    
- bei guter Durchmischung kurze Pulse möglich
    

Das musst du empirisch testen, aber als Stromsparprinzip ist es sinnvoll.

## Sensorik: was wirklich rein sollte

Pflicht für v1:

- **Temperatur**
    
- **pH**
    
- **optische Biomasse-/OD-Schätzung**
    
- **Lichtsensor**
    
- **Akkuspannung / Strom / SoC**
    
- **Tankfüllstand grob**
    
- **Druck/Entgasung nur simpel**, kein High-End
    

Sehr sinnvoll:

- 1 kleine Kamera oder Mikroskop-Add-on für Wartung
    
- Luftpumpen-Strom als indirekter Funktionscheck
    

Nicht zuerst:

- DO-Sonde in Vollausbau
    
- komplexe Spektralsensorik
    
- zu viele Laborfeatures im Feldgerät
    

## Steuerlogik für maximalen Nutzen pro Wh

Ich würde das System in drei Energiemodi bauen:

### Mode 1 – Survival / Low Power

- 8–10 h Licht
    
- minimale Luftung
    
- nur Kernsensoren
    
- Telemetrie selten
    

### Mode 2 – Standard

- 12–14 h Licht
    
- normale Luftung
    
- Logging regelmäßig
    

### Mode 3 – Sun Rich

- 14 h Licht oder höhere Intensität
    
- häufigeres Logging
    
- Pumpzyklen großzügiger
    

Die Regelgröße ist nicht nur Uhrzeit, sondern:

- Akkustand
    
- eingehende Solarleistung
    
- Tanktemperatur
    
- Biomassezustand
    

## Mechanisches Box-Konzept

In deiner Gehäusegröße würde ich das intern so aufteilen:

### Linke Sektion

- Akku
    
- MPPT
    
- BMS
    
- Sicherungen
    
- DC-DC
    

### Mittlere Sektion

- flacher Kulturtank
    
- LED-Seitenprofile
    
- Sensorfenster / OD-Pfad
    
- Luftlift
    

### Rechte Service-Sektion

- Pi Zero
    
- Sensorboard
    
- Peristaltik
    
- Luftpumpe
    
- sterile Filter
    
- Ernte-/Mediumkartusche
    

Das trennt Wärme, Elektronik und Biologie halbwegs sauber.

## Was ich für v1 ausdrücklich vermeiden würde

- 24/7 Vollbeleuchtung
    
- dicker Rundtank
    
- integriertes Heizelement mit hoher Leistung
    
- fest verklebte, schwer reinigbare Innenräume
    
- zu viele Arten gleichzeitig
    
- Marketingclaim „versorgt 1–3 Personen täglich“
    

## Wie ich das Produkt stattdessen positionieren würde

Nicht:

- „portable complete nutrition reactor“
    

Sondern:

- **portable fresh microalgae supplement unit**
    
- **autonomous expedition nutrition add-on**
    
- **field-ready live spirulina pilot system**
    

Das ist technisch glaubwürdig und später besser ausbaufähig.

## Meine klare v1-Empfehlung

Wenn ich es auf einen Satz verdichte:

**Flacher 1,5–2,0-L-Arthrospira-Reaktor, 2+1-seitige dimmbare LED-Beleuchtung, 12–14h adaptive Photoperiode, kleine gefilterte Luftlift-Pumpe, Pi-Zero-Steuerung, 12V-LiFePO4 mit externem 60W-Faltpanel.**

Damit optimierst du auf:

- Stabilität
    
- Stromersparnis
    
- Reinigbarkeit
    
- echte Feldtauglichkeit
    

Nicht auf Maximalertrag.

Als Nächstes kann ich dir daraus ein **komplettes v1-MVP-Dokument** machen:  
mit Blockdiagramm, Bauraumaufteilung, Leistungsbudget, Betriebsmodi und Testplan.

  

Bewerte die idee. mehrwert, umsetzung, etc. in welche richtungen kann das projekt entwickelt werden? macht es sinn?

  

Kurz gesagt: **Ja, die Idee macht Sinn — aber nur in der richtigen Formulierung und Zielsetzung.**  
Als „autonomes Mikronährstoff-Add-on“ ist sie **plausibel, differenzierend und ausbaufähig**.  
Als „mobile Vollversorgung für 1–3 Personen“ wäre sie technisch und regulatorisch sehr schwer haltbar.

Ich bewerte das jetzt ehrlich und nüchtern — aus **Produkt-, Technik- und Strategie-Perspektive**.

---

# 🧠 1. Kernbewertung (klar & direkt)

## Gesamturteil

👉 **8/10 als Konzept**  
👉 **5/10 als direktes Produkt (ohne Anpassung)**  
👉 **9/10 als Plattform / Systemidee**

---

# 💡 2. Mehrwert – ist das wirklich sinnvoll?

## 🟢 Echter Mehrwert (stark!)

### 1. Autarke Mikronährstoffquelle

- frische Mikroalgen vor Ort
    
- unabhängig von Lieferketten
    
- besonders relevant für:
    
    - Expedition
        
    - Remote Work
        
    - Forschung
        
    - Krisenszenarien
        

👉 Das ist **kein Gimmick**, sondern echtes Problem-Solution-Fit.

---

### 2. „Live Food“ statt gelagertes Supplement

- kein Pulver
    
- kein Verfall durch Lagerung
    
- kontinuierliche Produktion
    

👉 Das ist ein **emotional + funktional starkes Alleinstellungsmerkmal**.

---

### 3. Systemdenken statt Einzelprodukt

Du baust:

👉 **kein Gerät, sondern ein autarkes Bio-System**

Das ist extrem wertvoll für:

- ESN / dein größeres Projekt
    
- AI + Bio Integration
    
- nachhaltige Systeme
    

---

### 4. Sichtbarkeit / Storytelling

Das Produkt ist:

- visuell spannend (lebende Kultur)
    
- erklärbar
    
- „wow“-fähig
    

👉 riesiger Vorteil für:

- Kickstarter
    
- Social Media
    
- Demos
    

---

## 🔴 Wo der Mehrwert überschätzt werden kann

### „Ernährung für 1–3 Personen“

👉 unrealistisch in dieser Größe

Gefahr:

- falsche Erwartungen
    
- Vertrauensverlust
    

---

### „gesund = automatisch sicher“

👉 nein

- Kontamination
    
- Toxine
    
- Schwermetalle
    

👉 hier brauchst du klare Kommunikation

---

# ⚙️ 3. Technische Machbarkeit

## 🟢 Gut machbar

- 1–3 L stabiler Reaktor
    
- Luftsystem
    
- Sensorik
    
- Pi-basierte Steuerung
    
- Solar + Akku
    
- LED-Lichtsystem
    

👉 alles in deinem Skillset + DIY machbar

---

## 🟡 Herausfordernd

### Energie vs. Licht

- größter Bottleneck
    

### Temperaturkontrolle

- Outdoor sehr variabel
    

### Kontamination

- mobil deutlich schwieriger
    

---

## 🔴 Kritisch

### Food Safety

- ohne externe Tests kein echtes „essbar“-Claim
    

### Langzeitstabilität

- 3–5 Tage: realistisch
    
- Wochen: schwierig ohne Wartung
    

---

# 🧠 4. Markt & Positionierung

## 🟢 Gute Zielgruppen

### 1. Expedition / Outdoor / Prepper

👉 dein primärer Sweet Spot

---

### 2. Biohacker / Health / Longevity

👉 „live spirulina“ ist interessant

---

### 3. Maker / Nerd / DIY Community

👉 sehr stark

---

### 4. Bildung / Forschung

👉 Schulen, Unis, Labs

---

## 🟡 Schwieriger

### Militär / Front

👉 Anforderungen extrem hoch  
👉 Zertifizierung schwierig  
👉 eher langfristig

---

# 🚀 5. Produkt-Richtungen (sehr wichtig)

Das ist der spannendste Teil.

---

## 🔷 Richtung 1 – „Explorer Unit“ (empfohlen für v1)

👉 dein aktuelles Konzept

- tragbar
    
- robust
    
- autark
    
- 1–2 L
    
- Fokus: Stabilität
    

**Ziel:**

- Demonstration
    
- Feldtest
    
- erste Nutzer
    

---

## 🔷 Richtung 2 – „Daily Supplement Station“

👉 stationär oder semi-mobil

- 5–10 L
    
- bessere Lichtfläche
    
- mehr Output
    

**Ziel:**

- echte tägliche Nutzung
    
- Home / Vanlife / Research
    

---

## 🔷 Richtung 3 – „Modular System“

👉 sehr spannend langfristig

- zentrale Power Unit
    
- mehrere Reaktor-Module
    

**Ziel:**

- skalierbar
    
- austauschbar
    
- wartbar
    

---

## 🔷 Richtung 4 – „Smart Bio-System“ (dein Vorteil!)

👉 hier bist du besonders stark

- Sensorik
    
- AI (ABrain)
    
- automatische Optimierung
    

**Ziel:**  
👉 selbstoptimierende Bio-Produktion

---

## 🔷 Richtung 5 – „Platform / Ecosystem“

👉 langfristig extrem wertvoll

- verschiedene Algenarten
    
- verschiedene Anwendungen:
    
    - Protein
        
    - Pigmente
        
    - Omega-3
        

👉 dein System wird zur Plattform

---

# 🧠 6. Differenzierung (wichtig!)

Was dich wirklich besonders macht:

---

## 🔥 Kombination aus:

- Hardware (Reaktor)
    
- Software (Logging + AI)
    
- Biologie (Algen)
    
- Autarkie (Solar)
    

👉 Diese Kombination ist selten.

---

# ⚠️ 7. Hauptrisiken

## 1. Overengineering

👉 zu komplex für v1

---

## 2. falsche Positionierung

👉 „Ernährungssystem“ vs „Supplement-System“

---

## 3. Hygiene / Wartung

👉 unterschätzt

---

## 4. Energiebedarf

👉 unterschätzt

---

## 5. Erwartung vs Realität

👉 wichtig für Produktvertrauen

---

# 🧠 8. Macht es Sinn?

## 👉 Ja, wenn du es so definierst:

**Ein tragbares, autonomes Mikroalgen-System zur kontinuierlichen Produktion kleiner, frischer Supplement-Mengen in abgelegenen Umgebungen.**

---

## 👉 Nein, wenn du es so definierst:

**Ein Gerät, das 1–3 Personen täglich vollständig ernährt.**

---

# 🚀 9. Meine klare Empfehlung

## Baue NICHT sofort ein Produkt.

Baue:

👉 **einen extrem guten Prototyp v1**

---

## Ziele für v1

- läuft 3–5 Tage stabil
    
- produziert kontinuierlich Biomasse
    
- keine Kontamination
    
- Energie funktioniert
    
- Daten sind sauber
    

---

## Danach

- testen
    
- messen
    
- realistische Outputzahlen bestimmen
    
- Positionierung darauf basieren
    

---

# 🧠 Fazit

Du hast hier:

👉 eine **echte, sinnvolle Idee**  
👉 mit **klarem Mehrwert**  
👉 und **starkem Differenzierungspotenzial**

Aber:

👉 der Erfolg hängt komplett davon ab,  
wie ehrlich und präzise du sie positionierst.

---

# 👉 Wenn du willst (nächster Schritt)

Ich kann dir jetzt bauen:

### Option A

👉 **MVP Produkt-Konzept (inkl. Features, Preis, Zielgruppe)**

### Option B

👉 **Technisches Blockdiagramm + Komponentenliste v1**

### Option C

👉 **Kickstarter-/Pitch-Story (extrem stark für dein Projekt)**

---

Ich würde dir empfehlen:

👉 **MVP Produkt-Konzept als nächstes**

  

Ein tragbares, autonomes Mikroalgen-System zur kontinuierlichen Produktion kleiner, frischer Supplement-Mengen in abgelegenen Umgebungen. Explorer Unit Daily Supplement Station Modular System Smart Bio-System Plattform/Ecosystem

  

Sehr gut — jetzt hast du im Grunde schon die **richtige Produktlinie definiert**.  
Ich mache daraus jetzt ein **sauberes, skalierbares Produkt- und Systemkonzept**, das du direkt weiterentwickeln oder pitchen kannst.

---

# 🌱 Produktvision (klar formuliert)

**Ein tragbares, autonomes Mikroalgen-System zur kontinuierlichen Produktion kleiner, frischer Supplement-Mengen in abgelegenen Umgebungen.**

👉 Das ist **präzise, glaubwürdig und stark**.

---

# 🧠 1. SYSTEMDENKEN (das ist dein eigentlicher Vorteil)

Du baust **kein einzelnes Produkt**, sondern ein:

👉 **Bio-Produktions-Ökosystem**

bestehend aus:

Hardware + Biologie + Energie + Daten + AI

👉 Genau das macht dein Projekt besonders.

---

# 🧱 2. PRODUKTLINIE (klar strukturiert)

Ich baue dir deine 5 Richtungen jetzt sauber aus:

---

## 🔷 1. Explorer Unit (v1 – Einstieg)

👉 Dein aktueller Fokus

### 🎯 Zweck

- mobile Nutzung
    
- Expedition / Outdoor / Remote Work
    
- Demonstration & MVP
    

---

### ⚙️ Eigenschaften

- 1–2 L Kultur
    
- 3–5 Tage autonom
    
- Solar + Akku
    
- minimalistische Sensorik
    
- stabile Arthrospira/Spirulina Kultur
    

---

### 💡 Positionierung

👉 „Portable Live Spirulina Unit“

---

### 💥 Stärke

- einfach
    
- robust
    
- sofort baubar
    
- gutes Storytelling
    

---

## 🔷 2. Daily Supplement Station

👉 erste echte Nutzstufe

### 🎯 Zweck

- tägliche Nutzung für 1 Person
    
- stationär / Vanlife / Research
    

---

### ⚙️ Eigenschaften

- 5–10 L Kultur
    
- bessere Lichtfläche
    
- stabilere Umgebung
    
- optional automatisierte Ernte
    

---

### 💡 Positionierung

👉 „Personal Microalgae Supplement System“

---

### 💥 Stärke

- realer Nutzen
    
- echte Routine möglich
    

---

## 🔷 3. Modular System

👉 hier wird es richtig spannend

### 🎯 Zweck

- skalierbar
    
- wartbar
    
- flexibel
    

---

### ⚙️ Architektur

[Power Unit] + [Reaktor Module x N]

---

### Module

- Bio-Reaktor-Kassetten
    
- Energie-Module
    
- Sensor-Module
    

---

### 💡 Positionierung

👉 „Modular Bio Production System“

---

### 💥 Stärke

- skalierbar
    
- austauschbar
    
- langlebig
    

---

## 🔷 4. Smart Bio-System

👉 dein größter Differenzierungsfaktor

### 🎯 Zweck

- automatische Optimierung
    
- Fehlererkennung
    
- datengetriebene Steuerung
    

---

### ⚙️ Features

- Sensorik (OD, pH, Temp)
    
- AI-Bildanalyse
    
- automatische Regelung:
    
    - Licht
        
    - Luft
        
    - Dosierung
        

---

### 💡 Positionierung

👉 „Self-Optimizing Bio Reactor“

---

### 💥 Stärke

👉 DAS ist dein USP

---

## 🔷 5. Plattform / Ecosystem

👉 langfristig das größte Potenzial

---

### 🎯 Vision

Ein System für:

- verschiedene Algen
    
- verschiedene Outputs:
    
    - Protein
        
    - Omega-3
        
    - Pigmente
        
    - Spezialstoffe
        

---

### ⚙️ Komponenten

- Hardware Plattform
    
- Software / API
    
- AI Layer
    
- Community / Daten
    

---

### 💡 Positionierung

👉 „Distributed Bio Production Platform“

---

### 💥 Stärke

👉 extrem skalierbar (technisch + wirtschaftlich)

---

# 🧠 3. EVOLUTION (wie sich das entwickelt)

Explorer → Station → Modular → Smart → Platform

👉 das ist deine Roadmap

---

# ⚙️ 4. TECHNISCHE ROADMAP

---

## Phase 1 – Explorer MVP

- stabiler 1–2 L Reaktor
    
- Licht + Luft optimiert
    
- Energie funktioniert
    
- keine Kontamination
    
- einfache Sensorik
    

---

## Phase 2 – Messbarkeit

- Spectrophotometer integriert
    
- Logging
    
- Dashboard
    

---

## Phase 3 – Automatisierung

- Regelkreise:
    
    - Licht
        
    - Luft
        
    - Dosierung
        

---

## Phase 4 – AI

- Bildanalyse
    
- Anomalie-Erkennung
    
- Empfehlungen
    

---

## Phase 5 – Plattform

- mehrere Module
    
- API
    
- Daten-Netzwerk
    

---

# 💡 5. WICHTIGSTE DESIGN-ENTSCHEIDUNGEN

---

## 🔥 1. Flacher Reaktor statt Tank

👉 wichtigste Entscheidung überhaupt

---

## 🔥 2. Energie zuerst denken

👉 alles muss sich daran orientieren

---

## 🔥 3. Stabilität > Output

👉 besonders für v1

---

## 🔥 4. Ein Organismus zuerst

👉 Spirulina/Arthrospira

---

## 🔥 5. Modular denken

👉 spart dir später massive Probleme

---

# 🧠 6. DEIN USP (wirklich wichtig)

Du kombinierst:

- Bioreaktor
    
- Autarkie (Solar)
    
- Sensorik
    
- AI (ABrain)
    
- Modularität
    

👉 Diese Kombination gibt es so kaum.

---

# ⚠️ 7. KRITISCHE RISIKEN

---

## 1. Overclaim

👉 „Ernährungssystem“ vermeiden

---

## 2. Hygiene

👉 unterschätzt

---

## 3. Energie

👉 realistisch planen

---

## 4. Komplexität

👉 v1 so simpel wie möglich

---

# 🚀 8. STRATEGISCHE EMPFEHLUNG

---

## 👉 Baue zuerst:

### Explorer Unit v1

**Ziel:**

- funktioniert zuverlässig
    
- läuft mehrere Tage
    
- produziert messbare Biomasse
    

---

## 👉 Danach:

- Daten sammeln
    
- reale Output-Zahlen
    
- echte Limits verstehen
    

---

## 👉 Dann:

- Daily Station
    
- Modular System
    

---

# 🧠 FAZIT

👉 Ja, das Projekt macht Sinn  
👉 Ja, es hat echten Mehrwert  
👉 Ja, es kann ein Produkt werden

Aber:

👉 nur wenn du es als **System + Plattform** denkst  
👉 und nicht als einzelnes „Wundergerät“

---

# 👉 Nächster sinnvoller Schritt

Jetzt wird es konkret:

### Option A

👉 **Explorer Unit v1 – detaillierter Bauplan (mechanisch + elektrisch + Energiebudget)**

### Option B

👉 **Produkt-MVP Konzept (Preis, Zielgruppe, Features, Story)**

### Option C

👉 **Pitch / Kickstarter Konzept (extrem wichtig für dich)**

---

Ich würde dir ganz klar empfehlen:

👉 **Explorer Unit v1 Bauplan als nächstes**

  

Ich stelle mir ein Ecosystem, aus verschiedenen Modulen vor. Mobil und dtationär. Die Mobilen Module sollen auch stationär verwendet werden können. ein modulares System, aus Reakor-Kasetten, ca 420x180x160mm größe vor, jedes modul incl eigener energie versorgung und sensorik, dazu (optional) ein zentrales Energie-Modul. dazu soll es größere, stationäre Module geben, Daily Dupplement Station, Smart Bio-System.

  

Ja — **genau so wird daraus ein ernstzunehmendes System**.

Das ist viel stärker als „ein einzelner mobiler Reaktor“:  
Du denkst bereits in einer **Produktfamilie mit gemeinsamer Plattform**. Das macht technisch, strategisch und später auch wirtschaftlich deutlich mehr Sinn.

Ich würde das so strukturieren:

# Systemvision

Ein **modulares Mikroalgen-Ökosystem** aus:

- **mobilen Reaktor-Kassetten**
    
- **optionalem zentralen Energie-Modul**
    
- **größeren stationären Einheiten**
    
- **gemeinsamer Sensorik-, Software- und Steuerplattform**
    

Wichtiger Grundsatz:

**Jedes mobile Modul ist allein lauffähig, wird aber stärker im Verbund.**

Das ist die richtige Architektur.

# Warum diese Richtung stark ist

Sie löst mehrere Probleme gleichzeitig:

Erstens:  
Ein einzelnes Gerät ist immer ein Kompromiss zwischen Tragbarkeit, Output, Wartung und Energie.

Zweitens:  
Mit Modulen kannst du das System passend aufbauen:

- 1 Modul für Expedition
    
- 2–3 Module für Vanlife / Basecamp
    
- mehrere Module mit Zentralenergie für stationären Betrieb
    

Drittens:  
Du baust damit nicht nur Hardware, sondern eine **skalierbare Plattform**.

# Mein Architekturvorschlag

Ich würde die Produktfamilie in **4 Ebenen** gliedern.

## 1. Mobile Reactor Cassette

Das ist das Kernmodul.

Format grob wie von dir genannt:

- ca. **420 × 180 × 160 mm**
    

Jede Kassette enthält:

- flachen Reaktor
    
- LED-Licht
    
- Luftsystem
    
- Grundsensorik
    
- Mikrocontroller / Pi Node
    
- Akku
    
- Ladeelektronik
    
- lokalen Ernte-/Serviceport
    

Ziel:

- eigenständig betreibbar
    
- tragbar
    
- einzeln wartbar
    
- stationär andockbar
    

Das ist die wichtigste Einheit im ganzen System.

## 2. Central Energy Module

Optionales Systemmodul für Verbundbetrieb.

Enthält:

- größeren Akku
    
- MPPT / Solar-Management
    
- DC-Bus
    
- ggf. stärkere Rechen-/Kommunikationseinheit
    
- Ladeports für mobile Kassetten
    
- Energieverteilung
    

Ziel:

- mehrere Reaktor-Kassetten versorgen
    
- stationären Betrieb stabilisieren
    
- Solar effizienter nutzen
    
- Wartung vereinfachen
    

Wichtig:  
Die Kassetten dürfen **nie davon abhängig** sein.  
Das Energie-Modul ist ein **Booster**, kein Single Point of Failure.

## 3. Daily Supplement Station

Stationäres System für echten Alltagsnutzen.

Größer:

- mehr Kulturvolumen
    
- bessere Lichtfläche
    
- stärkere Luft-/Flüssigkeitsführung
    
- bessere Reinigung
    
- optional teilautomatische Ernte
    

Ziel:

- täglicher Supplement-Betrieb
    
- stationär zuhause / im Labor / in Basecamps
    
- real deutlich sinnvoller als die mobilen Einheiten für kontinuierliche Nutzung
    

## 4. Smart Bio System

Die High-End-Schicht.

Zusätzlich zu Hardware:

- zentrale Datenplattform
    
- AI-Bildanalyse
    
- adaptive Lichtsteuerung
    
- Anomalie-Erkennung
    
- Freigabe-Logik
    
- Wartungsempfehlungen
    
- Reaktorvergleich
    
- Flottenmanagement mehrerer Module
    

Das ist nicht ein separates Gerät, sondern die **intelligente Ebene über allem**.

# Der wichtigste Designgrundsatz

Du brauchst einen **gemeinsamen Plattformstandard**.

Also gleiche Standards für:

- Strom
    
- Daten
    
- Sensorik
    
- Ports
    
- Halterungen
    
- Software
    
- Gehäusephilosophie
    
- Wartungslogik
    

Wenn du das früh sauber definierst, sparst du dir später extrem viel Chaos.

# Was standardisiert werden sollte

## Mechanisch

- gleiche Außenmaße für mobile Kassetten
    
- gleiche Befestigungspunkte
    
- gleiche Stapel-/Dockinglogik
    
- gleiche Servicezugänge
    

## Elektrisch

- ein gemeinsamer Spannungsbus, z. B. 12 V
    
- definierte Ladeports
    
- definierte Absicherung
    
- einheitliche Steckverbinder
    

## Daten

- jedes Modul hat eigene ID
    
- gleiches MQTT-Topic-Schema
    
- gleiche Sensor-Namen
    
- gleiches Telemetrieformat
    

## Biologisch

- standardisierte Reaktor-Kassetten je Kulturklasse
    
- standardisierte Reinigungszyklen
    
- standardisierte Medienlogik
    
- standardisierte Freigabekriterien
    

# Meine empfohlene Produktfamilie

Ich würde das nicht nur „mobil vs stationär“ nennen, sondern klar staffeln.

## A. Reactor Cassette S

Die echte mobile Einheit.

Ziel:

- Expedition
    
- Outdoor
    
- Feldlabor
    
- Demonstration
    

Merkmale:

- 1–2 L Kultur
    
- eigener Akku
    
- Sensorik
    
- lokale Steuerung
    
- tragbar
    

## B. Reactor Cassette M

Gleiche Plattform, aber etwas mehr Volumen oder bessere Lichtfläche.

Ziel:

- Vanlife
    
- kleine stationäre Nutzung
    
- Research
    
- längere autarke Phasen
    

## C. Dock / Energy Base

Stationäres Andocksystem.

Ziel:

- mehrere Kassetten gleichzeitig laden und betreiben
    
- größere Solaranbindung
    
- Datenhub
    
- Netzbetrieb optional
    

## D. Daily Supplement Station

Eigenständige stationäre Hauptmaschine.

Ziel:

- täglicher Einsatz
    
- besserer Output
    
- niedrigere Kosten pro Gramm Biomasse
    
- weniger Kompromisse
    

## E. Smart Bio Layer

Software-/AI-Schicht für alles.

# So greifen die Systeme ineinander

Das Schöne ist:

- Die **Explorer Unit** ist einfach eine einzelne Reactor Cassette S.
    
- Mehrere Kassetten + Energy Base ergeben ein **Modular System**.
    
- Die Daily Supplement Station ist die stationäre, optimierte Linie.
    
- Das Smart Bio System ist die gemeinsame Intelligenz über allen Produkten.
    

Dadurch bleibt die gesamte Familie logisch konsistent.

# Meine klare Empfehlung für die mobile Kassette

Ich würde die mobile Kassette intern in 5 Zonen aufteilen.

## 1. Bio-Zone

- flacher Reaktor
    
- Luftlift / Diffusor
    
- Entgasungsraum
    
- Ernteport
    
- Reinigungsport
    

## 2. Licht-Zone

- zwei Hauptlichtseiten
    
- eine schwächere Korrekturseite
    
- Kühlprofile
    
- reflektive oder absorbierende definierte Innenflächen
    

## 3. Energie-Zone

- Akku
    
- BMS
    
- Ladeelektronik
    
- Solar-Eingang
    
- Sicherungen
    

## 4. Control-Zone

- Pi Zero / ESP
    
- ADC
    
- Sensor-Hub
    
- Datenspeicher
    
- Funk / kabelgebundene Schnittstellen
    

## 5. Service-Zone

- Luftfilter
    
- Peristaltik
    
- Schlauchmanagement
    
- Schnellwechsel-Komponenten
    

Diese Trennung ist wichtig für Wartbarkeit und Hygiene.

# Was ich an deinem Ansatz besonders gut finde

Die Idee, dass **mobile Module auch stationär verwendbar** sind, ist extrem stark.

Das bringt dir:

- weniger Produktchaos
    
- bessere Wiederverwendbarkeit
    
- leichteren Einstieg für Nutzer
    
- Upgrade-Pfade statt Wegwerfprodukt
    
- schönes Ökosystemdenken
    

Das ist viel besser als zwei komplett getrennte Welten zu bauen.

# Wo du aufpassen musst

Es gibt ein paar Risiken.

## 1. Zu viel Funktion in einem Modul

Wenn jede mobile Kassette alles maximal können soll, wird sie:

- zu teuer
    
- zu schwer
    
- zu komplex
    
- zu wartungsintensiv
    

Darum:  
**Mobile Kassetten müssen minimalistisch und robust bleiben.**

## 2. Zu viele Kulturarten am Anfang

Bitte nicht das ganze Ecosystem erst für fünf Arten optimieren.

Erst:

- eine Kultur
    
- ein Reaktortyp
    
- ein Standard
    

Danach ausweiten.

## 3. Modulgrenzen unscharf

Wenn nicht klar ist, was Kassette, Dock und Station jeweils leisten, verwischt das Produktprofil.

# Meine strategische Lesart

Du entwickelst hier eigentlich drei Dinge gleichzeitig:

1. **ein physisches Produkt**
    
2. **eine modulare Hardwareplattform**
    
3. **eine Daten-/AI-Bioplattform**
    

Und genau darin liegt der eigentliche Wert.

# Ein möglicher Namensrahmen

Nur als Arbeitsstruktur:

- **Cassette S** – mobile Explorer-Kassette
    
- **Cassette M** – größere modulare Kassette
    
- **Energy Dock** – zentrale Energie-/Datenbasis
    
- **Daily Station** – stationäre Supplement-Einheit
    
- **BioOS / Smart Layer** – Steuerung, Dashboard, AI, Freigabe
    

# Mein Urteil

**Ja, das macht sehr viel Sinn.**

Nicht nur als Einzelidee, sondern vor allem als:

- modulare Produktlinie
    
- technische Plattform
    
- langfristiges Ecosystem
    

Die Richtung ist deutlich stärker als ein Einzelgerät, weil sie:

- realistischer skalierbar ist
    
- besser zu deinem Systemdenken passt
    
- klarere Upgrade-Wege schafft
    
- echten Plattformwert erzeugt
    

# Was ich dir als Nächstes empfehlen würde

Der sinnvollste nächste Schritt ist jetzt nicht mehr lose Ideensammlung, sondern eine **harte Plattformdefinition**.

Also ein Dokument mit:

- Modulklassen
    
- gemeinsame Standards
    
- Pflicht-/Optionalkomponenten
    
- Docking-Logik
    
- Energiearchitektur
    
- Datenarchitektur
    
- Roadmap v1 bis v3
    

Ich kann dir das direkt als **ARCHITECTURE.md für das gesamte Ökosystem** ausarbeiten.

  

Welche Maße empfielst du für die Reaktor-Kasetten? Wie schwer wird eine Reaktor Kasette ca, das gewicht ist wichtig. Wie groß/gewicht/kapazität hat ein lifepo akku mit ca 120x180x160mm?

  

Ich rechne das jetzt von zwei Seiten auf: erst sinnvolle Kassettenmaße aus Biologie + Service + Gewicht, dann was in deinem Akku-Bauraum realistisch an LiFePO4-Kapazität und Masse drin ist. Der Akku ist dabei sehr wahrscheinlich der größte Gewichtstreiber der mobilen Kassette.

Ja — und **das Gewicht wird sehr wahrscheinlich der wichtigste harte Designparameter** für die mobile Kassette.

Mein klares Urteil vorweg:

- **Die Außenmaße 420 × 180 × 160 mm sind für eine mobile Kassette gut.**
    
- Für die **mobile Variante** würde ich **nicht auf 3 L**, sondern eher auf **ca. 1,2–1,8 L Kulturvolumen** optimieren.
    
- Mit Akku, Kultur, Gehäuse, Licht und Technik landest du realistisch eher bei **ca. 5,5–8,0 kg pro Kassette**.
    
- Wenn du wirklich tragbar und feldtauglich bleiben willst, würde ich **unter 7 kg als Ziel** setzen.
    

## 1. Welche Maße ich für die Reaktor-Kassette empfehlen würde

Dein Vorschlag **420 × 180 × 160 mm** ist als Außenmaß sinnvoll, weil er:

- noch tragbar bleibt,
    
- genug Fläche für einen flachen Reaktor bietet,
    
- Akku, Elektronik und Servicebereich überhaupt erst zulässt.
    

Ich würde die mobile Kassette in diesem Größenrahmen ungefähr so aufteilen:

- **Bio-Zone:** ca. 260–300 mm Länge
    
- **Energie-/Control-Zone:** ca. 100–130 mm Länge
    
- **Service-/Luft-/Pumpen-Zone:** ca. 40–60 mm Länge
    

Für den eigentlichen Reaktor würde ich **keinen dicken Tank**, sondern eine **flache Reaktorkammer** vorsehen, etwa mit:

- **aktive Reaktorfläche:** ca. **280 × 140 mm**
    
- **Lichtweg / Tiefe:** ca. **30–40 mm**
    

Das ergibt brutto ungefähr:

- 280 × 140 × 30 mm ≈ **1,18 L**
    
- 280 × 140 × 40 mm ≈ **1,57 L**
    
- 300 × 140 × 40 mm ≈ **1,68 L**
    

Das ist für eine mobile Kassette deutlich realistischer als 2,5–3 L, weil kurze Lichtwege für Mikroalgenprozesse viel günstiger sind als dicke Volumenkörper. PBR-Reviews heben Lichtweg und belichtete Fläche genau als zentrale Limitierungen hervor.

## 2. Meine Empfehlung für die mobilen Kassettenklassen

Ich würde drei mobile Größen nicht parallel bauen, sondern **eine Plattformgröße** und darin zwei Innenausbauten.

### Mobile Cassette S

- Außenmaß: **420 × 180 × 160 mm**
    
- Kulturvolumen: **1,2–1,6 L**
    
- Zielgewicht: **5,5–6,8 kg**
    

Das wäre meine klare Empfehlung für **Explorer / Feld / Outdoor**.

### Mobile Cassette M

- gleiches Außenmaß
    
- stärker auf Netz-/Dockbetrieb optimiert
    
- Kulturvolumen: **1,6–2,2 L**
    
- Zielgewicht: **6,5–8,0 kg**
    

Das ist eher **semi-mobil**, nicht mehr „angenehm tragbar“.

### Alles darüber

Sobald du mit dieser Bauform wirklich Richtung **2,5–3 L plus vernünftiger Energie** gehst, wird die Kassette sehr wahrscheinlich zu schwer und thermisch schwieriger. Dann lohnt eher ein **Dock-/Stationsmodus**.

## 3. Wie schwer wird eine Reaktor-Kassette ungefähr?

Die großen Massenblöcke sind:

### Kultur

1 Liter Kultur wiegt näherungsweise fast wie Wasser:

- **1,2 L ≈ 1,2 kg**
    
- **1,6 L ≈ 1,6 kg**
    
- **2,0 L ≈ 2,0 kg**
    

### Akku

Dazu gleich detailliert, aber grob:

- **20 Ah LiFePO4:** ca. **2,4–2,6 kg**
    
- **30 Ah LiFePO4:** ca. **3,0–3,4 kg**
    
- **40 Ah LiFePO4:** ca. **4,8–6,0 kg**, je nach Bauform
    

### Rest der Kassette

Für Reaktor, Gehäuse, LEDs, Pumpe, Sensorik, Halter, Filter, Verkabelung, Elektronik und etwas Strukturreserve würde ich grob rechnen mit:

- **1,5–2,3 kg**
    

### Daraus ergibt sich realistisch

#### S-Kassette mit 1,2–1,6 L + 20 Ah

- Kultur: **1,2–1,6 kg**
    
- Akku: **2,4–2,6 kg**
    
- Rest: **1,5–2,3 kg**
    
- **gesamt: ca. 5,1–6,5 kg**
    

#### S/M-Kassette mit 1,5–2,0 L + 30 Ah

- Kultur: **1,5–2,0 kg**
    
- Akku: **3,0–3,4 kg**
    
- Rest: **1,6–2,4 kg**
    
- **gesamt: ca. 6,1–7,8 kg**
    

#### Kassette mit 2,0 L + 40 Ah

- Kultur: **2,0 kg**
    
- Akku: **4,8–6,0 kg**
    
- Rest: **1,7–2,5 kg**
    
- **gesamt: ca. 8,5–10,5 kg**
    

Mein Fazit dazu:  
**Für „tragbar“ ist 20 Ah sehr attraktiv, 30 Ah noch okay, 40 Ah wird in dieser Klasse schnell zu schwer.**

## 4. Was passt in einen LiFePO4-Bauraum von 120 × 180 × 160 mm?

Dein Akku-Bauraum hat:

- **120 × 180 × 160 mm**
    
- Volumen: **3,456 Liter**
    

Das klingt erstmal viel, aber mit BMS, Gehäuse, Kabeln, Haltern und Sicherheitsreserve ist das nicht riesig.

### Was sicher und entspannt passt

Ein **12V / 20Ah LiFePO4-Pack** passt sehr gut in diesen Raum.  
Beispiel: Bioenno nennt für 12V 20Ah etwa **160 × 108 × 83 mm** bei **2,4 kg**; eine ABS-Variante liegt bei etwa **182 × 77 × 171 mm** und **2,6 kg**, wobei diese Höhe deine 160 mm knapp überschreiten würde.

### Was mit guter Planung machbar sein kann

Ein **12V / 30Ah Pack** ist in dieser Größenordnung **grenzwertig, aber realistisch**, wenn du sauber packst oder ein passendes schmales Pack wählst.  
Beispiele:

- **180 × 76 × 166 mm**, **3,44 kg**
    
- **180 × 76 × 166 mm**, **3,0 kg**
    

Dein Bauraum ist aber **120 × 180 × 160 mm**, also:

- 180 mm Länge passt,
    
- 120 mm Breite passt,
    
- **160 mm Höhe** ist der kritische Punkt.
    

Das heißt:

- ein Standard-30Ah-Pack mit **166–168 mm Höhe** ist **für 160 mm nominell zu hoch**,
    
- ein **Custom-Pack** oder eine flachere Pack-Geometrie wäre dafür sinnvoller.
    

### Was eher nicht mehr sinnvoll passt

Ein typischer **12V / 40Ah LiFePO4-Pack** ist meist zu lang, zu hoch oder zu schwer für diesen Bauraum:

- Beispiel **197 × 130 × 168 mm**, **4,83 kg** — das überschreitet alle drei Grenzmaße teilweise.
    
- Ein anderer 40Ah-Pack liegt bei **223 × 95 × 175 mm** und ist ebenfalls größer als dein Bauraum.
    

## 5. Was ist mit einem selbst aufgebauten Pack aus prismatischen Zellen?

Für Custom-Packs ist das spannender.

Beispielsweise:

- **EVE LF50K**: **50 Ah**, **185,3 × 135,3 × 29,3 mm**, **1,395 kg pro Zelle**
    
- **EVE LF105**: **105 Ah**, **130,3 × 36,3 × 200,5 mm**, **1,98 kg pro Zelle**
    

Ein 12,8-V-Pack braucht 4 Zellen in Serie.

### Problem im 120 × 180 × 160-mm-Bauraum:

- **LF105** fällt wegen **200,5 mm Zellhöhe** praktisch raus.
    
- **LF50K** ist sehr attraktiv von der Energie, aber mit **185,3 mm Höhe** ebenfalls knapp über deinem 180-/160-mm-Rahmen.
    
- Eine **60-Ah-Zelle** mit etwa **130 × 36 × 190 mm** und **1,65 kg** wäre ebenfalls zu hoch.
    

Das heißt:  
**In genau diesem Bauraum sind Standard-Prismatics >30Ah oft geometrisch unpraktisch.**  
Für 20–30Ah bist du mit fertigen Flachpacks oder kleineren Zellformaten sehr wahrscheinlich besser dran.

## 6. Meine klare Akku-Empfehlung für die mobile Kassette

### Beste Balance: 12V / 20Ah LiFePO4

- Gewicht: etwa **2,4–2,6 kg**
    
- Energie: ca. **256 Wh**
    
- passt gut in deinen Bauraum
    
- trägt die mobile Kassette nicht unnötig hoch
    

Das ist mein Favorit für:

- Explorer Unit
    
- echte Tragbarkeit
    
- 1,2–1,6 L Kultur
    
- Solar-unterstützten Betrieb
    

### Zweite Wahl: 12V / 30Ah LiFePO4

- Gewicht: etwa **3,0–3,4 kg**
    
- Energie: ca. **384 Wh**
    
- sehr interessant, aber dein Bauraum ist dafür **zu knapp**, wenn du nur Standardpacks nimmst
    

Das wäre gut, wenn du:

- den Akku-Bauraum leicht vergrößerst,
    
- oder ein flacheres Custom-Pack nutzt.
    

### Nicht meine Empfehlung für die mobile Kassette: 40Ah

- meist **4,8 kg+**
    
- geometrisch in deinem Bauraum unpraktisch
    
- Gesamtgewicht der Kassette wird schnell unattraktiv.
    

## 7. Meine Maßempfehlung in einem Satz

Für die **mobile Reactor Cassette** würde ich festlegen:

- **Außenmaß:** 420 × 180 × 160 mm
    
- **Bio-Reaktor:** ca. 280–300 × 140 × 30–40 mm
    
- **Kulturvolumen:** **1,2–1,8 L**
    
- **Akkuziel:** **12V 20Ah**, optional **30Ah nur mit angepasstem Packdesign**
    
- **Zielgewicht:** **5,5–6,8 kg**, absolute Oberkante **~7,5 kg**
    

## 8. Mein strategischer Rat

Wenn Gewicht für dich wirklich kritisch ist, dann ist die beste Entscheidung nicht „mehr Akku“, sondern:

- **Reaktor flach halten**
    
- **20Ah als Standard**
    
- **größere Autarkie über externes Faltpanel oder Dock**
    
- **30Ah/40Ah in das zentrale Energie-Modul auslagern**
    

Das passt perfekt zu deiner Plattformidee:

- mobile Kassette bleibt leicht,
    
- Dock/Base liefert Reichweite,
    
- stationäre Systeme tragen die schweren Akkus.
    

Wenn du willst, mache ich dir als Nächstes eine **Gewichts- und Bauraum-Matrix für Cassette S / Cassette M / Energy Dock** mit konkreten Sollwerten pro Modul.

  

Ich strebe für die Mobile Cassette S volgendes an: Außenmaß: 420 × 180 × 160 mm Kulturvolumen: 1,2–1,6 L Zielgewicht: Max 3,5-4kg

  

Ich prüfe jetzt nüchtern, ob 3,5–4 kg mit deinen Zielmaßen überhaupt erreichbar ist — vor allem mit Kultur + Akku + Licht. Der Engpass wird fast sicher die Energiereserve sein, nicht der Reaktor selbst.

Mit **1,2–1,6 L Kultur** und **max. 3,5–4,0 kg Gesamtgewicht** ist die **Mobile Cassette S nur dann realistisch**, wenn du sie sehr konsequent auf **Leichtbau + kleines Akku-Pack + Solar/Dock-Unterstützung** auslegst.

Der harte Punkt ist simpel:  
**Die Kultur selbst wiegt schon 1,2–1,6 kg.**  
Dann bleiben dir für **Akku + Gehäuse + Reaktor + LEDs + Luftpumpe + Sensorik + Elektronik + Schläuche + Halter** nur noch etwa **1,9–2,8 kg**. Das ist machbar, aber nur mit klaren Kompromissen.

## Mein klares Urteil

**Ja, 3,5–4,0 kg ist machbar.**  
Aber nur, wenn du die Kassette so definierst:

- **1,2–1,4 L** als realistischer Sweet Spot, nicht 1,6 L als Standard
    
- **12V LiFePO4 eher 12 Ah**, maximal **15 Ah**
    
- keine schwere Voll-ABS-/Industrie-Batterie
    
- kein dickwandiger Tank
    
- kein thermisches Komfortsystem
    
- keine übergroße Luftpumpe
    
- Solar/Dock als fester Teil des Konzepts
    

**Wenn du 1,6 L + 20 Ah + robuste Gehäusestruktur willst, wirst du sehr wahrscheinlich über 4 kg landen.**

## Gewichtsbudget, das ich dir empfehlen würde

### Zielkonfiguration für unter 4 kg

Bei **1,2–1,4 L Kultur**:

- Kultur: **1,2–1,4 kg**
    
- Akku: **1,5–1,6 kg** bei 12V/12Ah LiFePO4
    
- restliches System: **0,9–1,0 kg**
    

Dann liegst du grob bei:

- **3,6–4,0 kg**
    

Das ist sportlich, aber realistisch.

### Konfiguration mit 20 Ah

Ein 12V/20Ah LiFePO4-Pack wiegt typischerweise etwa **2,4–2,6 kg**. Ein Beispiel liegt bei **160 × 108 × 83 mm und 2,4 kg**, ein anderes bei **182 × 77 × 171 mm und 2,6 kg**.

Mit **1,2–1,6 kg Kultur** wärst du damit schon bei:

- **3,6–4,2 kg nur aus Kultur + Akku**
    

Dann fehlt noch das ganze restliche Gerät.  
Darum ist **20 Ah für dein 4-kg-Ziel praktisch zu schwer**.

## Was das für die Akkuwahl bedeutet

Für deine Zielklasse würde ich so priorisieren:

### Beste Wahl: 12V / 12Ah LiFePO4

Ein 12Ah-LiFePO4 liegt typischerweise bei etwa **1,5–1,6 kg** und Abmessungen wie **215 × 56 × 79 mm**, **152 × 100 × 95 mm** oder **108 × 108 × 75 mm**.

Das ist für dein Gewichtsziel die sinnvollste Klasse.

### Noch denkbar: 12V / 15Ah LiFePO4

Bioenno nennt für ein 15Ah-Pack etwa **150 × 102 × 100 mm** bei **1,53 kg**. Das ist überraschend nah an 12Ah und deshalb für dich sehr interessant, wenn die reale Verfügbarkeit/Packform passt.

### Nicht passend für dein Zielgewicht: 20Ah+

20Ah liegt schon bei **2,4–2,6 kg**. Für eine 4-kg-Kassette ist das zu viel.

## Wie groß/kapazitätsstark ist ein LiFePO4-Akku in 120 × 180 × 160 mm?

Dein Bauraum von **120 × 180 × 160 mm** ist volumetrisch groß genug für **12Ah, 15Ah und manche 20Ah-Packs**. Die Frage ist weniger der Platz als das Gewicht.

### Was gut hineinpasst

- **12Ah**: sicher
    
- **15Ah**: sehr wahrscheinlich
    
- **20Ah**: geometrisch teilweise ja, gewichtlich für deine Kassette nein
    

### Was ich daraus ableite

Nur weil **20Ah** in den Bauraum passt, heißt das nicht, dass es ins **Gewichtsziel** passt.

## Wie viel Energie bekommst du dann?

Grob:

- **12V 12Ah ≈ 144 Wh nominal**
    
- **12V 15Ah ≈ 180 Wh nominal**
    
- **12V 20Ah ≈ 240 Wh nominal**
    

Praktisch nutzbar liegt etwas darunter, je nach Entladetiefe, Wandlern und Temperatur.

Da typische LiFePO4-Systeme meist grob im Bereich **90–160 Wh/kg** liegen, passen diese Zahlen auch gut zu den oben genannten Gewichten; neuere/optimierte Packs können höher liegen, aber darauf würde ich für ein robustes Feldprodukt nicht blind optimieren.

## Was bedeutet das für deine Autarkie?

Mit **12Ah** oder **15Ah** musst du die Kassette als **energieoptimiertes Modul** denken, nicht als „viel interne Reserve“.

Das heißt konkret:

- LEDs sind der Hauptverbraucher
    
- Luftpumpe klein und effizient
    
- Sensoren zyklisch statt dauernd
    
- Pi Zero statt größerer Pi
    
- Display vermeiden oder nur kurz aktiv
    
- Solar/Dock als Standard mitdenken
    

Anders gesagt:  
**Die 4-kg-Kassette funktioniert eher als intelligentes, sparsames Feldmodul — nicht als komplett energiefettes Standalone-System.**

## Meine Maß- und Volumenempfehlung für dein Ziel

Wenn du **unter 4 kg** bleiben willst, würde ich die Kassette so definieren:

### Außenmaß

- **420 × 180 × 160 mm**
    

### Ziel-Kulturvolumen

- **Nominal 1,2–1,4 L**
    
- **1,6 L nur als Stretch-Ziel**, nicht als harte Spezifikation
    

### Akku

- **12V 12Ah Standard**
    
- optional **12V 15Ah Pro-Version**
    

### Zielgewicht

- **Standard: 3,6–3,9 kg**
    
- **harte Oberkante: 4,0 kg**
    

## Was du dafür konstruktiv tun musst

Um das zu schaffen, musst du aktiv auf Leichtbau gehen:

### 1. Reaktor

- flache Reaktorkammer
    
- dünnwandige transparente Platte statt massiver Tank
    
- kurze Lichttiefe, nicht mehr Volumen „erzwingen“
    

### 2. Akku

- PVC-/leichte Packbauform statt schwerem Hartgehäuse
    
- Akku als austauschbares Modul denken
    

### 3. Gehäuse

- kein schweres Vollgehäuse
    
- Rippen-/Rahmenbauweise
    
- 3D-Druck nur dort, wo nötig
    

### 4. Licht

- 2 Hauptseiten + 1 schwache Korrekturseite
    
- keine überdimensionierten LED-Arrays
    

### 5. Elektronik

- Pi Zero
    
- kleine ADC-/Sensorboards
    
- keine unnötigen Verbraucher
    

## Meine ehrliche Bewertung deines Ziels

**4 kg max ist ein sehr gutes Ziel**, weil es die mobile Kassette diszipliniert.

Es zwingt dich zu:

- echter Modularität,
    
- Solar-/Dock-Denken,
    
- flachem Reaktordesign,
    
- stromsparender Steuerung.
    

**3,5 kg** ist möglich, aber nur als sehr optimierte Minimalversion.  
**4,0 kg** ist aus meiner Sicht das deutlich realistischere Ziel.

## Meine klare Empfehlung

Ich würde die Spezifikation so schreiben:

**Mobile Cassette S**

- Außenmaß: **420 × 180 × 160 mm**
    
- Ziel-Kulturvolumen: **1,2–1,4 L**
    
- Akku: **12V LiFePO4 12Ah Standard**, **15Ah optional**
    
- Zielgewicht: **3,6–4,0 kg**
    
- Designprinzip: **voll autark betreibbar, aber für Solar/Dock optimiert**
    

Das ist technisch glaubwürdig.

Als Nächstes kann ich dir daraus eine **harte Gewichts- und Bauteilmatrix** machen mit:

- Sollgewicht pro Baugruppe
    
- Akkuoptionen
    
- Energiebudget pro Tag
    
- „geht / geht nicht“-Varianten für Cassette S.
    

  

Warum 12v, ist 5v nicht besser?

  

Gute Frage — und genau hier triffst du eine **Grundsatzentscheidung für dein gesamtes System**.

Kurz gesagt:

👉 **5 V ist nicht „besser“, sondern nur für bestimmte Teile sinnvoll.**  
👉 Für dein System ist **12 V klar die bessere Hauptspannung**.

Ich erkläre dir das sauber und praxisnah.

---

# ⚡ 1. Der wichtigste Unterschied

## 5 V System

- niedrige Spannung
    
- hoher Strom nötig
    

## 12 V System

- höhere Spannung
    
- deutlich weniger Strom
    

👉 Leistung ist immer:

P = U × I

---

## Beispiel (10 W LED)

### Bei 5 V:

- Strom = **2 A**
    

### Bei 12 V:

- Strom = **0,83 A**
    

👉 Das ist ein riesiger Unterschied in einem kompakten System.

---

# 🔥 2. Warum 12 V für dein Projekt besser ist

---

## 🟢 1. Weniger Verluste

Hoher Strom bedeutet:

- dickere Kabel
    
- mehr Wärme
    
- Spannungsabfall
    
- ineffizient
    

👉 5 V = ineffizient bei Leistung  
👉 12 V = deutlich effizienter

---

## 🟢 2. Deine Hauptverbraucher sind NICHT 5 V

Du hast:

- LED-Beleuchtung
    
- Luftpumpe
    
- ggf. Ventile
    
- ggf. Heizung
    

👉 Diese Dinge sind fast immer:

- **12 V oder höher optimiert**
    

---

## 🟢 3. Solar passt perfekt zu 12 V

- 12 V Panels → Standard
    
- MPPT Controller → Standard
    
- LiFePO4 → Standard (12,8 V)
    

👉 5 V ist hier ein Fremdkörper

---

## 🟢 4. Akku-Systeme sind 12 V-nativ

LiFePO4:

- 4 Zellen → **12,8 V nominal**
    

👉 5 V bedeutet:

- Step-Down IMMER nötig
    
- zusätzliche Verluste
    

---

## 🟢 5. Skalierung (wichtig für dein Ecosystem!)

Du willst:

- mehrere Module
    
- Docking
    
- zentrale Energie
    

👉 Das geht mit 12 V sauber

Mit 5 V:

- zu hohe Ströme
    
- unpraktisch
    
- schlecht skalierbar
    

---

# 🔴 3. Warum 5 V alleine problematisch ist

---

## ❌ 1. Strom wird zu hoch

Beispiel:

- 20 W System bei 5 V → **4 A**
    
- mehrere Module → schnell >10 A
    

👉 das ist unpraktisch und ineffizient

---

## ❌ 2. Kabel werden dick & warm

- mehr Gewicht
    
- mehr Verluste
    
- schlechter für dein 4-kg-Ziel
    

---

## ❌ 3. Pumpen & LEDs passen nicht

Du müsstest:

- Step-Up bauen
    
- oder spezielle Hardware suchen
    

👉 unnötige Komplexität

---

# 🧠 4. Die richtige Architektur (Best Practice)

👉 NICHT entweder 5 V oder 12 V

👉 sondern:

## 🔷 Hybrid-System

12V (Hauptsystem)  
   ↓  
DC-DC Step-Down  
   ↓  
5V (Elektronik)

---

## 🔷 12 V versorgt:

- LEDs
    
- Luftpumpe
    
- ggf. Ventile
    
- ggf. Heizung
    

---

## 🔷 5 V versorgt:

- Raspberry Pi
    
- Sensoren
    
- ADC
    
- Kamera
    

---

👉 Das ist der Standard in fast allen mobilen Systemen.

---

# ⚙️ 5. Konkrete Empfehlung für dich

---

## 🔋 Hauptbus

👉 **12 V LiFePO4**

---

## 🔌 5 V Versorgung

👉 Step-Down:

- 12V → 5V
    
- effizient (90–95%)
    

---

## 🧠 Architektur

Akku (12V)  
   ↓  
Verteiler  
   ↓  
 ├── LED (12V)  
 ├── Pumpe (12V)  
 └── DC-DC → 5V → Pi + Sensoren

---

# 🧠 6. Gewicht & Effizienz (wichtig für dich)

Wenn du auf 5 V gehst:

- mehr Strom
    
- mehr Wärme
    
- mehr Kabelgewicht
    
- schlechtere Effizienz
    

👉 genau das Gegenteil von deinem Ziel (4 kg!)

---

# 🚀 7. Wann 5 V sinnvoll ist

Nur hier:

- kleine Sensoren
    
- Mikrocontroller
    
- Pi
    
- USB Geräte
    

👉 **niemals als Hauptsystemspannung**

---

# 🧠 Fazit

👉 **12 V ist die richtige Basis für dein System**

👉 **5 V ist nur eine Nebenversorgung**

---

# 🧭 Ein Satz zum Mitnehmen

👉  
**„Energie läuft auf 12 V – Intelligenz läuft auf 5 V“**

---

# 👉 Nächster sinnvoller Schritt

Jetzt können wir dein System richtig konkret machen:

### Option A

👉 **Elektrisches Gesamtschema (Akku, BMS, DC-DC, Sicherungen)**

### Option B

👉 **Energieverbrauchsrechnung pro Tag (realistisch!)**

### Option C

👉 **Komponentenliste (konkret kaufbar)**

---

Ich würde dir empfehlen:

👉 **Energieverbrauchsrechnung als nächstes**

  

Elektrisches Gesamtschema (Akku, BMS, DC-DC, Sicherungen) Und 👉 Energieverbrauchsrechnung pro Tag (realistisch!)

  

Ich mache dir das jetzt als belastbares v1-Stromkonzept: einmal die elektrische Architektur, dann ein realistisches Tagesbudget mit mehreren Betriebsmodi. Dabei rechne ich so, dass du sofort siehst, was unter 4 kg wirklich drin ist und wo die Hauptverbraucher sitzen.

Ja — ich mache dir das als **v1-Architektur für die Mobile Cassette S** mit:

- **12,8 V LiFePO4 als Hauptbus**
    
- **5 V als Nebenversorgung** für Pi/Sensorik
    
- **sauber abgesicherten Lastzweigen**
    
- **realistischem Tagesverbrauch** in 3 Modi
    

Wichtiger Ausgangspunkt: Ein 4-zelliges LiFePO4-System ist typischerweise **12,8 V nominal**, und viele LFP-Systeme werden im oberen Bereich um **14,4 V** geladen; für dein Design heißt das: Der 12-V-Bus ist in Wahrheit ein **ca. 10–14,6-V-Arbeitsbereich**, und alle Komponenten müssen das sauber vertragen.

# 1. Elektrisches Gesamtschema

## Zielarchitektur

[ Faltpanel 40–60 W ]  
          │  
          ▼  
[ MPPT-Laderegler ]  
          │  
          ▼  
[ 4S LiFePO4 Akku 12,8 V ]  
          │  
          ▼  
[ Hauptsicherung nahe Akku ]  
          │  
          ▼  
[ Power Distribution Board / DC Bus ]  
   ├── Sicherung 1 → LED-Treiber 12 V / PWM  
   ├── Sicherung 2 → Luftpumpe 12 V  
   ├── Sicherung 3 → Peristaltikpumpe 12 V  
   ├── Sicherung 4 → 12V→5V DC-DC Buck  
   │                    ├── Raspberry Pi Zero 2 W  
   │                    ├── ADC / Sensorhub  
   │                    ├── pH / Temp / Licht / Drucksensoren  
   │                    └── Kamera optional  
   └── Sicherung 5 → Reserve / Dock / Service Port  
  
[ BMS ]  
- Zellschutz  
- Überstrom  
- Unterspannung  
- Balancing

## Warum diese Struktur sinnvoll ist

Die stromstarken Verbraucher sind bei dir klar:

- LED-Beleuchtung
    
- Luftpumpe
    
- Peristaltik
    

Die gehören direkt auf den **12-V-Bus**.  
Der Pi Zero 2 W und Sensoren laufen besser über einen **separaten 5-V-Buck-Konverter**, weil der Pi eben 5 V braucht und DC/DC-Wandler in dieser Klasse typischerweise Wirkungsgrade bis in die Mitte der 90-%-Region erreichen können. Mean Well nennt bei kompakten DC/DC-Wandlern je nach Serie **bis zu 95 %** und bei LED-Treibern sogar **bis zu 97 %**.

# 2. Empfohlene elektrische Blöcke

## A. Akku

Für dein Gewichtsfenster würde ich v1 so setzen:

- **Standard:** 4S LiFePO4 **12 Ah**
    
- **Optional Pro:** 4S LiFePO4 **15 Ah**
    

Das ist die realistischste Klasse, wenn du unter 4 kg bleiben willst. Größere 20-Ah-Packs wiegen typischerweise eher **2,4–2,6 kg**, was dein Gesamtgewicht zu stark belastet.

## B. BMS

Pflichtfunktionen:

- Overcharge
    
- Overdischarge
    
- Overcurrent
    
- Kurzschluss
    
- Zellbalancing
    

Für Produktreife würde ich das BMS **nicht optional**, sondern integralen Akkuteil machen.

## C. Hauptsicherung

Direkt **so nah wie möglich am Akku-Plus**.

Für Cassette S v1 würde ich grob mit einem maximalen Gesamtstrom im Bereich von **5–8 A** rechnen. Deshalb:

- **Hauptsicherung:** etwa **10 A träge** als v1-Arbeitsgröße
    

Nicht weil du dauernd 10 A brauchst, sondern damit Anlaufströme und Reserven abgedeckt sind, ohne die Schutzwirkung zu verlieren.

## D. Einzelsicherungen / Lastzweige

Vorschlag:

- LED-Zweig: **3 A**
    
- Luftpumpe: **1 A**
    
- Peristaltik: **1 A**
    
- 5-V-Buck/Pi-Zweig: **2 A**
    
- Reserve/Service: **1 A**
    

Das sind Startwerte; die finale Größe hängt von den echten Komponenten ab.

## E. 12V→5V Buck

Der Pi Zero 2 W ist offiziell als stromsparendes Board positioniert, und im Raspberry-Pi-Forum wird für den Zero 2 W ein typischer aktiver Strom um **350 mA bei 5 V** genannt; in stark optimierten Szenarien wurden auch rund **1,06–2,07 W** gemessen. Daraus ergibt sich: Plane konservativ mit **0,5–1,0 W idle-light** und **1,5–2,5 W aktiv** für Pi + Grundsystem.

Darum würde ich nehmen:

- **5-V-Buck mit 3 A Ausgang**
    
- sauber gekühlt
    
- low-noise
    
- undervoltage-fest
    

Das ist für Pi + Sensorik + Reserve gut.

# 3. Konkretes v1-Schaltschema in Funktionsblöcken

## Energiepfad

Solar In  
  → MPPT  
    → Akku (4S LiFePO4)  
      → Hauptsicherung  
        → Verteilerbus 12 V  
          → LED Driver  
          → Air Pump MOSFET / Relay  
          → Peristaltic Pump MOSFET / Relay  
          → 5V Buck  
              → Pi Zero 2 W  
              → ADS1115 / I2C  
              → Sensoren  
              → Kamera optional

## Steuerpfad

Der Pi schaltet nicht direkt „roh“ Leistung, sondern:

- GPIO → Gate-Treiber/MOSFET
    
- MOSFET → Pumpe / LED Enable / Peristaltik
    

Damit bleibt die Logik sauber von der Last getrennt.

## Sicherheitslogik

- Akku-Unterspannung → Lastprofil auf Eco
    
- Akku sehr niedrig → Pumpen nur Minimalbetrieb, LEDs gedimmt
    
- Sensorfehler → auf sicheren Default
    
- Druckfehler/Entgasungsfehler → Warnung / Abschaltung bestimmter Funktionen
    

# 4. Realistische Energieverbrauchsrechnung pro Tag

Jetzt der wichtige Teil.

Ich rechne dir drei Modi:

- **Eco**
    
- **Normal**
    
- **Sun-Rich / Boost**
    

Damit kannst du später sauber gegen Akku und Solar auslegen.

## Annahmen für v1

### LED

Für eine flache 1,2–1,4-L-Kassette mit 2+1-Lichtseiten würde ich für v1 grob ansetzen:

- **nominale LED-Leistung:** 8–12 W
    
- aber **nicht dauernd auf Vollgas**
    

### Luftpumpe

- kleine 12-V-Membranpumpe
    
- **ca. 0,8–1,5 W** Dauer-/Taktbetrieb
    

### Peristaltik

- nur kurz aktiv
    
- im Tagesmittel meist klein
    

### Pi + Sensorik

- Pi Zero 2 W + Sensoren + ADC + Logging
    
- **ca. 1,0–2,0 W** realistisch als Dauerbudget, je nach Aktivität und Kameraeinsatz.
    

### DC/DC- und Systemverluste

- etwa **10–15 % Systemaufschlag** ist eine sinnvolle v1-Arbeitsannahme
    

---

## Modus 1: Eco

### LED

- 6 W mittlere Leistung
    
- 10 h pro Tag  
    = **60 Wh/Tag**
    

### Luftpumpe

- 1,0 W
    
- 24 h  
    = **24 Wh/Tag**
    

### Pi + Sensorik

- 1,2 W
    
- 24 h  
    = **28,8 Wh/Tag**
    

### Peristaltik

- 5 W
    
- 10 min/Tag  
    = **0,8 Wh/Tag**
    

### Verluste / DC-DC / Reserve

- pauschal **~12 Wh/Tag**
    

### Summe Eco

= **ca. 126 Wh/Tag**

---

## Modus 2: Normal

### LED

- 8 W mittlere Leistung
    
- 12 h  
    = **96 Wh/Tag**
    

### Luftpumpe

- 1,2 W
    
- 24 h  
    = **28,8 Wh/Tag**
    

### Pi + Sensorik

- 1,5 W
    
- 24 h  
    = **36 Wh/Tag**
    

### Peristaltik

- 5 W
    
- 15 min/Tag  
    = **1,25 Wh/Tag**
    

### Verluste / Reserve

- **~16 Wh/Tag**
    

### Summe Normal

= **ca. 178 Wh/Tag**

---

## Modus 3: Sun-Rich / Boost

### LED

- 10 W mittlere Leistung
    
- 14 h  
    = **140 Wh/Tag**
    

### Luftpumpe

- 1,5 W
    
- 24 h  
    = **36 Wh/Tag**
    

### Pi + Sensorik

- 1,8 W
    
- 24 h  
    = **43,2 Wh/Tag**
    

### Peristaltik

- 5 W
    
- 20 min/Tag  
    = **1,7 Wh/Tag**
    

### Verluste / Reserve

- **~20 Wh/Tag**
    

### Summe Boost

= **ca. 241 Wh/Tag**

# 5. Was heißt das für den Akku?

## 12V 12Ah LiFePO4

Nominal etwa:

- **12,8 V × 12 Ah = ~154 Wh**
    

Praktisch nutzbar würde ich konservativ mit etwas darunter planen.

### Reichweite

- Eco: etwa **1,2 Tage**
    
- Normal: **unter 1 Tag**
    
- Boost: deutlich **unter 1 Tag**
    

## 12V 15Ah LiFePO4

Nominal etwa:

- **12,8 V × 15 Ah = ~192 Wh**
    

### Reichweite

- Eco: etwa **1,5 Tage**
    
- Normal: knapp **1 Tag**
    
- Boost: **<1 Tag**
    

## Konsequenz

Für dein System ist der interne Akku **kein 3–5-Tage-Standalone-Akku**, sondern:

- Puffer
    
- Nachtbetrieb
    
- Schlechtwetterreserve
    
- Autarkie für kurze Phasen
    

Die 3–5 Tage erreichst du **nur sinnvoll mit Solarunterstützung und/oder Dock/Energy-Modul**.

# 6. Solar realistisch eingerechnet

Wenn du ein **60-W-Faltpanel** hast, erreichst du im Feld nicht dauerhaft 60 W. Realistisch ist deutlich weniger über den Tag gemittelt.

Eine grobe, vorsichtige Arbeitsannahme für Systemdesign ist:

- **40–60 W Panel**
    
- bei guten Bedingungen vielleicht **100–200 Wh/Tag** netto nutzbar
    
- bei mäßigen Bedingungen deutlich weniger
    

Darum ist dein System sinnvoll, wenn es:

- im **Eco-/Normalbereich** leben kann
    
- und Solar-/Dock-Energie den Tagesbedarf ganz oder teilweise abfängt
    

# 7. Was ich dir für Cassette S konkret empfehlen würde

## Elektrische Spezifikation v1

### Hauptbus

- **12,8 V LiFePO4 (4S)**
    

### Akku

- **Standard:** 12 Ah
    
- **Optional:** 15 Ah
    

### Laden

- MPPT mit LFP-Profil
    
- Bulk/Absorption im Bereich um **14,4 V** passend zum Batterietyp/BMS.
    

### 5-V-Versorgung

- 12V→5V Buck, **3 A**
    

### Tagesziele

- **Eco-Ziel:** ~125 Wh/Tag
    
- **Normal-Ziel:** ~175 Wh/Tag
    
- **Hartes Designziel für Optimierung:** unter **140 Wh/Tag**
    

# 8. Mein nüchternes Fazit

## Elektrisches Gesamtschema

Ja, das ist sauber als:

- **12-V-Hauptsystem**
    
- **5-V-Logikzweig**
    
- **abgesicherte Einzelzweige**
    
- **MPPT + LiFePO4 + BMS**
    
- **MOSFET-gesteuerte Lasten**
    

## Energieverbrauch

Realistisch liegt deine Cassette S wahrscheinlich bei:

- **~125 Wh/Tag in Eco**
    
- **~175 Wh/Tag normal**
    
- **~240 Wh/Tag in Boost**
    

## Wichtigste Designfolge

Wenn du unter 4 kg bleiben willst, ist die mobile Kassette **nur mit kleinem Akku sinnvoll**.  
Darum muss dein Gesamtsystem zwingend so gedacht sein:

- **Kassette = leichtes Smart-Modul**
    
- **Solar/Dock = Reichweitenverlängerung**
    
- **größere Akkureserven = ins Energy-Modul auslagern**
    

Das passt perfekt zu deiner Plattformidee.

Als Nächstes kann ich dir daraus direkt eine **Bauteilliste + Sicherungsplan + Kabelquerschnitt-Vorschlag + ASCII-Schaltplan** machen.

  

Bauteilliste + Sicherungsplan + Kabelquerschnitt-Vorschlag + ASCII-Schaltplan machen. Mit Komponentenliste (konkret kaufbar)

  

Ich ziehe das jetzt in eine belastbare v1-Stückliste: erst die Architektur und Absicherung, dann eine konkret kaufbare Beispielkonfiguration mit möglichst passenden Bauformen und realistischen Strompfaden. Schwerpunkt ist dabei: unter 4 kg bleiben, ohne elektrisch Murks zu bauen.

Ja — hier ist ein **konkretes v1-Paket** für die **Mobile Cassette S** mit 12,8-V-Hauptbus, 5-V-Nebenversorgung, abgesicherten Lastzweigen und einer **kaufbaren Beispielkonfiguration**. Ich optimiere dabei auf dein Ziel **3,5–4,0 kg**, also eher **12Ah-Klasse** statt 20Ah. Ein 12V-12Ah-LiFePO4-Pack liegt je nach Bauform grob bei **1,18–1,50 kg** und etwa **151×98×95 mm** bis **215×56×79 mm**; das passt deutlich besser zu deinem Gewichtsbudget als 20Ah.

# 1. Architektur v1

## Elektrisches Konzept

- **Hauptbus:** 4S LiFePO4, nominal **12,8 V**
    
- **Laden:** MPPT mit LiFePO4-Profil, z. B. **14,4 V Absorption**
    
- **Leistungszweige auf 12 V:** LED, Luftpumpe, Peristaltik
    
- **Logikzweig auf 5 V:** Pi Zero 2 W, ADC, Sensoren, optionale Kamera
    
- **Schalten:** MOSFETs oder passende DC-Lastschalter, nicht direkt über GPIO
    
- **Absicherung:** Hauptsicherung direkt am Akku, danach Einzelsicherungen pro Zweig
    

LiFePO4-12V-Systeme werden typischerweise um **14,4 V** geladen; der MPPT 75/10 von Victron ist für 12/24-V-Batterien ausgelegt, bietet Lastausgang und hat einen Spitzenwirkungsgrad von **98 %**.

# 2. ASCII-Schaltplan

                 +-----------------------------+  
                 |     Faltpanel 40–60 W      |  
                 +--------------+--------------+  
                                |  
                                v  
                    +------------------------+  
                    | MPPT 75/10 (LiFePO4)   |  
                    | Absorption ~14.4 V     |  
                    +-----------+------------+  
                                |  
                                v  
                      +----------------------+  
                      | 4S LiFePO4 12V 12Ah  |  
                      | mit integriertem BMS |  
                      +----------+-----------+  
                                 |  
                                 |  (so kurz wie möglich)  
                                 v  
                       [ Hauptsicherung 10 A ]  
                                 |  
                                 v  
                  +----------------------------------+  
                  | 12 V Power Distribution / Busbar |  
                  +----+-----------+---------+-------+  
                       |           |         |   
                       |           |         |  
              [3 A ATO Fuse] [1 A Fuse] [1 A Fuse]  
                       |           |         |  
                       v           v         v  
                LED-Treiber/   Luftpumpe  Peristaltik  
                PWM-MOSFET      12 V       12 V  
  
                       +---------------------------+  
                       |  
                [2 A ATO Fuse]  
                       |  
                       v  
                +--------------+  
                | 12V -> 5V    |  
                | Buck 3 A      |  
                +------+--------+  
                       |  
          +------------+--------------------+  
          |            |         |          |  
          v            v         v          v  
      Pi Zero 2 W   ADS1115    pH/Temp    Kamera opt.  
                               Licht/OD  
  
Optional:  
12 V Bus -> [1 A Reserve Fuse] -> Dock-Port / Service-Port

# 3. Sicherungsplan v1

Die Fuse-Auswahl hängt von **Normalstrom, Spannung, Umgebungstemperatur und Überlastverhalten** ab; bei Niedervolt-DC sind ATO/ATC-Blade-Fuses und passende 32-V-Inline-Halter eine pragmatische Wahl.

## Empfohlene Sicherungen

- **Hauptsicherung am Akku:** **10 A ATO/ATC oder MAXI**, je nach Halter
    
- **LED-Zweig:** **3 A**
    
- **Luftpumpe:** **1 A**
    
- **Peristaltik:** **1 A**
    
- **5-V-Buck / Logikzweig:** **2 A**
    
- **Reserve-/Dock-Port:** **1 A**
    

## Kaufbare Halter

- **Littelfuse FHAC0001ZXJL** – ATO Inline Fuse Holder, **20 A / 32 VDC**
    
- **Littelfuse FHAC1BP** – 20 A Inline Blade Fuse Holder
    
- Für höhere Hauptströme wäre auch ein MAXI-Halter wie **MAHC0001ZXJ** möglich, aber für Cassette S ist das meist nicht nötig.
    

# 4. Kabelquerschnitt-Vorschlag v1

Ampacity-Tabellen zeigen die **maximal sichere Strombelastbarkeit**, berücksichtigen aber **nicht automatisch den Spannungsabfall**; gerade bei 12-V-Systemen ist deshalb nicht nur der Strom, sondern auch die Leitungslänge wichtig.

Für deine kurzen Leitungswege in einer 420-mm-Kassette würde ich pragmatisch so gehen:

## Empfehlung

- **Akku -> Hauptsicherung -> Bus:** **1,5 mm²**
    
- **Bus -> LED-Zweig:** **0,75–1,0 mm²**
    
- **Bus -> Luftpumpe:** **0,5–0,75 mm²**
    
- **Bus -> Peristaltik:** **0,5–0,75 mm²**
    
- **Bus -> 5-V-Buck:** **0,75 mm²**
    
- **5 V zu Pi/Sensorik:** **0,25–0,5 mm²**
    
- **I²C / Signalleitungen:** **0,14–0,25 mm²**
    

## Warum so

- 12-V-Niederspannung profitiert von **etwas dickeren Leitungen**, um Spannungseinbruch an LED/Pumpe zu vermeiden
    
- 1,5 mm² für die Akkuzuleitung ist in deinem Maßstab leicht, robust und elektrisch entspannt
    
- 0,75 mm² ist für die meisten Zweige der gute Sweet Spot
    

# 5. Komponentenliste – konkret kaufbar

Ich liste dir bewusst **eine belastbare Beispielkonfiguration** auf, nicht zwanzig austauschbare Varianten.

## A. Akku

### Option 1 – leichter Standard

- **PowerBrick PRO+ 12V 12Ah LiFePO4**
    
- **151 × 98 × 95 mm**
    
- **1,30 kg**
    

### Option 2 – schlanke Packform

- **Bioenno 12V 12Ah LFP Battery (PVC Pack)**
    
- **215 × 56 × 79 mm**
    
- **1,5 kg**
    

### Option 3 – sehr leicht

- **WattCycle 12V 12Ah LiFePO4**
    
- **ca. 152 × 99 × 99 mm**
    
- **1,18 kg** laut Produktseite
    

**Meine Empfehlung:**  
Für die Cassette S würde ich **PowerBrick PRO+** oder **WattCycle** priorisieren, weil die Bauform kompakt ist und die Masse besser ins 4-kg-Ziel passt.

## B. MPPT-Laderegler

- **Victron SmartSolar MPPT 75/10**
    
- 12/24-V-Batterien
    
- Nennladestrom **10 A**
    
- nominelle PV-Leistung an 12 V: **145 W**
    
- Spitzenwirkungsgrad **98 %**
    
- Lastausgang vorhanden
    

**Empfehlung:**  
Für 40–60-W-Faltpanel ist der 75/10 technisch mehr als ausreichend.

## C. 12V->5V DC/DC

### Robuste Industrievariante

- **Mean Well SD-15A-5**
    
- Eingang **9,2–18 V**
    
- Ausgang **5 V / 3 A**
    
- **78 × 51 × 28 mm**
    

Wenn du mehr Reserve willst:

- **Mean Well SD-25A-5**
    
- **5 V / 5 A**
    
- größer und schwerer, für Cassette S meist unnötig.
    

## D. Rechen- und Steuerboard

- **Raspberry Pi Zero 2 W**
    
- **65 × 30 mm**
    
- Quad-Core 1 GHz
    
- 512 MB RAM
    

## E. Luftpumpe

- **Makeblock Air Pump Motor DC 12V/370-02PM**
    
- **<250 mA unter Last**
    
- **3,0 LPM**
    
- Größe **D27 × 65 mm**
    
- Gewicht **65 g**
    

Für Cassette S ist das fast ideal: klein, leicht, wenig Strom.

## F. LED-Licht

Für v1 würde ich **12-V-COB-LED-Strip** oder sparsamen 12-V-Strip nehmen, nicht starr mit Spezialmodulen starten.

### Datenpunkt für sinnvolle Klasse

- 12-V-COB-Strip, verfügbar in **5 / 10 / 15 W pro Meter**
    

**Empfehlung für Cassette S:**

- **3 Seiten Licht**
    
- je Seite etwa **25–30 cm**
    
- zusammen grob **0,75–0,9 m Strip**
    
- für v1 eher **5–10 W/m**, nicht 15 W/m
    

Damit bleibst du eher im **sparsame-Beleuchtung-Fenster**.

## G. Sicherungen / Halter

- **Littelfuse ATO 32 V Blade Fuses**
    
- **Littelfuse FHAC0001ZXJL** oder **FHAC1BP** Inline-Halter
    

## H. Sensorik / Peripherie

Für diese Teile brauchst du keine exotischen Industriekomponenten im ersten Wurf:

- **ADS1115** I²C ADC
    
- **DS18B20** Temperatur
    
- pH-Interface mit isoliertem Signalmodul
    
- optional Lichtsensor / einfacher Fotodiodenpfad
    
- OD-/Biomassepfad separat aufbauen
    

Für diese Sensorik reicht der 5-V-Nebenbus locker aus.

# 6. Realistische Stückliste v1

## Pflicht

- 1× **12V 12Ah LiFePO4 Akku**
    
- 1× **Victron SmartSolar MPPT 75/10**
    
- 1× **Raspberry Pi Zero 2 W**
    
- 1× **Mean Well SD-15A-5**
    
- 1× **12V Mini-Luftpumpe** (z. B. Makeblock 370-02PM)
    
- 1× **Peristaltikpumpe 12 V**
    
- 1× **LED Strip 12 V, 5–10 W/m**
    
- 1× **Hauptsicherungshalter**
    
- 4–5× **Inline-Sicherungshalter / Verteilersicherung**
    
- 1× **Power Distribution Board / Klemmleiste / Busbar**
    
- 1× **BMS** falls nicht im Akku integriert
    
- 1× **Hauptschalter**
    
- 1× **Solar-Eingangsstecker**
    
- 1× **Dock-/Service-Port**
    
- Litzen, Aderendhülsen, Crimps, Schrumpfschlauch
    

## Optional, aber sinnvoll

- 1× **INA219/INA226** oder ähnlicher Strom-/Spannungssensor
    
- 1× **MOSFET-Board** für LED/Pumpen
    
- 1× **Wartungs-USB-Port**
    
- 1× **kleine Status-LED / Summer**
    

# 7. Energieverbrauch pro Tag – realistische v1-Rechnung

Ich setze hier eine sparsame, aber nicht unrealistische Cassette S an.

## Annahmen

- LED-System: **0,8 m Strip**, effektiv etwa **6–8 W** im Mittel während der Lichtphase
    
- Luftpumpe: **0,25 A @ 12 V = 3 W Maximalleistung** wäre zu hoch angesetzt; aus dem Datenblatt ergibt sich **<250 mA**, also **<3 W**, realistisch eher **2–3 W Peak** und niedriger im Mittel, wenn getaktet.
    
- Pi Zero 2 W + Sensorik: etwa **1,5–2,5 W** im typischen Betrieb, je nach Logging/WLAN/Aktivität.
    

Damit komme ich für v1 auf drei Betriebsmodi:

## Eco

- LED: **6 W × 10 h = 60 Wh**
    
- Luftpumpe: **1,2 W × 24 h = 28,8 Wh**
    
- Pi + Sensorik: **1,5 W × 24 h = 36 Wh**
    
- Peristaltik: **5 W × 10 min ≈ 0,8 Wh**
    
- Verluste: **~10–12 Wh**
    

### Summe Eco

**ca. 136–138 Wh/Tag**

## Normal

- LED: **8 W × 12 h = 96 Wh**
    
- Luftpumpe: **1,5 W × 24 h = 36 Wh**
    
- Pi + Sensorik: **1,8 W × 24 h = 43,2 Wh**
    
- Peristaltik: **5 W × 15 min ≈ 1,25 Wh**
    
- Verluste: **~14 Wh**
    

### Summe Normal

**ca. 190 Wh/Tag**

## Sparsame Optimierung für echte Cassette-S-Ziele

Wenn du die LED weiter drosselst und die Luftpumpe taktest, kannst du näher an:

**ca. 110–130 Wh/Tag**

kommen. Das ist aus meiner Sicht das eigentliche Ziel für Cassette S.

# 8. Was das für den Akku bedeutet

Ein 12V-12Ah-LiFePO4 hat grob:

- **12,8 V × 12 Ah = 153,6 Wh nominal**
    

Das heißt praktisch:

- **ohne Solar** reicht die Cassette S **nicht** komfortabel für 3–5 Tage
    
- sie ist ein **smartes Modul mit Pufferakku**
    
- **Solar und/oder Dock** sind kein Luxus, sondern Teil des Konzepts
    

Das bestätigt deinen Plattformansatz:  
**leichte mobile Kassette + optionales Energy Module** ist der richtige Weg.

# 9. Meine klare Empfehlung für v1

## Beste Beispielkonfiguration

- **Akku:** PowerBrick PRO+ 12V 12Ah oder WattCycle 12V 12Ah
    
- **MPPT:** Victron SmartSolar 75/10
    
- **DC/DC:** Mean Well SD-15A-5
    
- **Controller:** Raspberry Pi Zero 2 W
    
- **Luft:** Makeblock 12V/370-02PM
    
- **Licht:** 12-V-COB-Strip, **5–10 W/m**, ca. **0,8 m**
    
- **Hauptsicherung:** 10 A
    
- **Zweigfuses:** 3 A LED, 1 A Pumpe, 1 A Peristaltik, 2 A 5V-Buck
    

## Kabel

- **1,5 mm²** Akku-Hauptweg
    
- **0,75–1,0 mm²** LED
    
- **0,5–0,75 mm²** Pumpen
    
- **0,25–0,5 mm²** 5-V-Verteilung
    

## Gewichtsziel

Mit leichtem 12Ah-Akku, flachem Reaktor und disziplinierter Mechanik ist **3,6–4,0 kg** weiter realistisch.

Als nächsten Schritt kann ich dir daraus direkt eine **tabellarische BOM mit Sollgewicht pro Baugruppe und geschätztem Preisrahmen** machen.