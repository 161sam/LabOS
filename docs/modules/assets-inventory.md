# Assets, Inventory, Labels

Drei zusammengehörige Module bilden die physische Objektebene des Labs ab.

## AssetOps / DeviceOps V1

Langlebige Geräte und Assets als operative Objekte — ohne ERP-, Einkaufs- oder CMDB-Ambitionen.

### Felder

- `name`, `asset_type`, `category`, `status`, `location`, `zone`
- optional: `serial_number`, `manufacturer`, `model`, `maintenance_notes`
- `last_maintenance_at`, `next_maintenance_at`
- `wiki_ref` (optionale Verlinkung ins Wiki)

### Endpoints

- `GET /api/v1/assets`, `GET /api/v1/assets/overview`, `GET /api/v1/assets/{id}`
- `POST /api/v1/assets`, `PUT /api/v1/assets/{id}`, `PATCH /api/v1/assets/{id}/status`
- Filter: `status`, `category`, `location`, `zone`

### Enums

- **asset_type:** `printer_3d`, `microscope`, `soldering_station`, `power_supply`, `pump`, `server`, `gpu_node`, `sbc`, `network_device`, `lab_device`, `tool`
- **status:** `active`, `maintenance`, `error`, `inactive`, `retired`

### Integrationen

- Tasks und Photos können über `asset_id` mit Assets verknüpft werden
- Dashboard-KPIs: aktive Assets, Wartungsfälle, Fehlerstatus, nächste Wartungen

### UI

`/assets` mit Liste, Filter, Create/Edit, Statuswechsel, Label-Zuordnung.

## Inventory / MaterialOps V1

Materialien, Verbrauchsgüter, Lagerlogik. Fokus: sichtbar machen, was vorhanden ist, wo es liegt und was knapp wird.

### Felder

- `name`, `category`, `status`, `quantity`, `unit`, `location`
- optional: `min_quantity`, `zone`, `supplier`, `sku`, `notes`, `wiki_ref`, `last_restocked_at`, `expiry_date`, `asset_id`
- automatische Ableitung: `low_stock` und `out_of_stock` aus `quantity` und `min_quantity`

### Endpoints

- `GET /api/v1/inventory`, `GET /api/v1/inventory/overview`, `GET /api/v1/inventory/{id}`
- `POST /api/v1/inventory`, `PUT /api/v1/inventory/{id}`, `PATCH /api/v1/inventory/{id}/status`
- Filter: `status`, `category`, `location`, `zone`, `search`, `low_stock=true`

### Enums

- **category:** `filament`, `electronic_component`, `cable`, `screw`, `tubing`, `chemical`, `nutrient`, `cleaning_supply`, `spare_part`, `consumable`, `storage_box_content`
- **status:** `available`, `low_stock`, `out_of_stock`, `reserved`, `expired`, `archived`

### Abgrenzung

- AssetOps beschreibt langlebige Geräte und Infrastruktur
- Inventory beschreibt Materialien, Verbrauchsgüter, Ersatzteile
- Beschaffung, Einkaufslisten, Batch-/Lot-Tracking sind **bewusst nicht** Teil von V1

### UI

`/inventory` mit Liste, Filter (inkl. `low_stock`), Dashboard-KPIs (Gesamtbestand, knappe Positionen, leere Positionen, kritische Materialien).

## QR / Label / Traceability V1

Reale Objekte direkt mit ihren digitalen Einträgen verbinden — ohne Scanner-Hardware oder Lagerbuchungen.

### Modell

Separates `Label`-Modell:

- `label_code`, `label_type` (`qr` | `printed_label`)
- `target_type` (`asset` | `inventory_item`), `target_id`
- optional: `display_name`, `location_snapshot`, `note`
- Aktiv/Inaktiv-Status

### Endpoints

- `GET /api/v1/labels`, `GET /api/v1/labels/overview`
- `GET /api/v1/labels/{label_code}`, `GET /api/v1/labels/{label_code}/target`, `GET /api/v1/labels/{label_code}/qr`
- `POST /api/v1/labels`, `PUT /api/v1/labels/{id}`, `PATCH /api/v1/labels/{id}/active`

### Nutzung

- QR-Code auf Asset oder Material zeigt auf scanfähige Browser-Seite unter `/scan/{labelCode}`.
- Objektseiten in `/assets` und `/inventory` zeigen zugehörige Labels.
- Label-Verwaltung erlaubt Reaktivierung, Stilllegung, Re-Targeting.

### QR-Ziele

- `PUBLIC_WEB_BASE_URL` steuert die Browser-Zieladresse für `/scan/{labelCode}` (Default `http://localhost:3000`)
- `PUBLIC_API_BASE_URL` steuert die ausgelieferten QR-/API-Links (Default `http://localhost:8000`)

### Bewusst noch nicht enthalten

- Barcode-Scanner-Integration
- mobile Native App
- Inventur-Workflow, Lagerbuchung
- Batch-/Lot-Tracking
- physische Etikettendrucker-Integration
