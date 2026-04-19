# Vision & Photos

Zwei zusammengehörige Module:

- **Foto Upload + Vision Basis V1** — lokales Storage, Metadaten, Objektverknüpfung
- **Vision Node / AI Integration V1** — Pillow-basierte Auto-Analyse

## Foto Upload + Vision Basis V1

Bilddateien werden lokal unter `storage/photos/YYYY/MM/` abgelegt; die Datenbank speichert nur Metadaten und den relativen `storage_path`. Keine BLOB-Speicherung in PostgreSQL.

**Erlaubte MIME-Typen:** `image/jpeg`, `image/png`, `image/webp`.
**Standard-Größenlimit:** `8 MiB` pro Upload.

### Photo-Felder

`filename`, `original_filename`, `mime_type`, `size_bytes`, `storage_path`, `title`, `notes`, `charge_id`, `reactor_id`, `asset_id`, `created_at`, `uploaded_by`, `captured_at`.

### Endpoints

- `GET /api/v1/photos` (Filter `charge_id`, `reactor_id`, `asset_id`, `latest`, `limit`)
- `GET /api/v1/photos/{id}`
- `POST /api/v1/photos/upload`
- `PUT /api/v1/photos/{id}`
- `GET /api/v1/photos/{id}/file`
- `GET /api/v1/photos/{id}/analysis-status`

Beispiel:

```bash
curl -b .labos-cookie.txt -X POST http://localhost:8000/api/v1/photos/upload \
  -F "file=@./example.png" \
  -F "title=Reaktor A1 Tagesbild" \
  -F "reactor_id=1"
```

### UI

- `/photos` mit Upload-Formular, Filter, Galerie, Detailansicht
- Dashboard zeigt Gesamtzahl, Uploads der letzten sieben Tage, letzte Uploads

## Vision Node / AI Integration V1

Lokale ML-freie Bildanalyse — jedes hochgeladene Foto wird automatisch ausgewertet und die Ergebnisse stehen in Photo-UI, ReactorOps-Twin und ABrain-Kontext zur Verfügung.

### Modell

`VisionAnalysis`:

- `photo_id`, `reactor_id`, `analysis_type` (Default `basic`)
- `status` (`ok` | `failed`), `result` (JSON), `confidence`, `error`, `created_at`
- Indizes über `photo_id`, `reactor_id`, `analysis_type`, `status`, `created_at`
- Migration `20260419_0016_vision_ai_integration_v1`

### Service

`services/api/app/services/vision.py` nutzt Pillow für:

- Auflösung, Durchschnitts-/Streuungs-RGB, Helligkeit, Schärfe, dominante Farbe
- Grün- / Braun-Anteil
- regelbasierte Klassifikation `health_label`: `healthy_green`, `growing`, `low_biomass`, `no_growth_visible`, `contamination_suspected`, `too_dark`, `overexposed`
- Konfidenz kombiniert Kontrast, Schärfe und Signal-Anteil
- Fehlerfälle (Datei fehlt, Bild defekt) werden als `status='failed'` persistiert; Upload bleibt unberührt

### Boundary

Vision ist **Feature Extraction + Classification only** (siehe [architecture.md](../architecture.md)). Keine automatischen Aktionen, keine Tasks/Commands aus einer Vision-Klassifikation — das entscheidet ABrain.

### Endpoints

- `GET /api/v1/vision/photos/{photo_id}` — neueste Analyse
- `GET /api/v1/vision/photos/{photo_id}/history` — komplette Historie
- `POST /api/v1/vision/analyze/{photo_id}` — manuelle Neu-Analyse (Operator)

### Integrationen

- `PhotoRead`, `PhotoAnalysisStatusRead`: `latest_vision`
- `ReactorTwinRead`: `latest_vision` je Reaktor
- ABrain-Kontext-Section `photos`: `vision_health_label`, `vision_green_ratio`, `vision_brown_ratio`, `vision_confidence`

### UI

- `/photos`: Galerie-Kacheln zeigen Health-Badge, Detailansicht zeigt Klassifikation, Konfidenz, Helligkeit, Schärfe, Grün-/Braun-Anteil, Ø- und dominante Farbe (Farb-Swatches).
- Button "Neu analysieren" triggert manuelle Re-Analyse.

### Bewusst noch nicht enthalten

- neuronale Modelle (torch, tensorflow, opencv-dnn)
- Segmentation oder Objekterkennung
- GPU-/Jetson-spezifische Beschleunigung
- mehrstufige Analyse-Pipelines oder Vergleichsmetriken über Zeit
