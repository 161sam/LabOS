export const chargeStatusOptions = [
  { value: 'planned', label: 'Geplant' },
  { value: 'active', label: 'Aktiv' },
  { value: 'paused', label: 'Pausiert' },
  { value: 'completed', label: 'Abgeschlossen' },
  { value: 'archived', label: 'Archiviert' },
] as const;

export const reactorStatusOptions = [
  { value: 'online', label: 'Online' },
  { value: 'offline', label: 'Offline' },
  { value: 'cleaning', label: 'Reinigung' },
  { value: 'maintenance', label: 'Wartung' },
] as const;

export const reactorPhaseOptions = [
  { value: 'inoculation', label: 'Inokulation' },
  { value: 'growth', label: 'Wachstum' },
  { value: 'stabilization', label: 'Stabilisierung' },
  { value: 'harvest_ready', label: 'Harvest Ready' },
  { value: 'maintenance', label: 'Wartung' },
  { value: 'paused', label: 'Pausiert' },
  { value: 'incident', label: 'Incident' },
] as const;

export const reactorTechnicalStateOptions = [
  { value: 'nominal', label: 'Nominal' },
  { value: 'warning', label: 'Warning' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'degraded', label: 'Degraded' },
  { value: 'error', label: 'Error' },
] as const;

export const reactorBiologicalStateOptions = [
  { value: 'stable', label: 'Stabil' },
  { value: 'adapting', label: 'Adapting' },
  { value: 'growing', label: 'Growing' },
  { value: 'stressed', label: 'Stressed' },
  { value: 'contaminated', label: 'Contaminated' },
  { value: 'unknown', label: 'Unknown' },
] as const;

export const reactorContaminationStateOptions = [
  { value: 'suspected', label: 'Suspected' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'recovering', label: 'Recovering' },
  { value: 'cleared', label: 'Cleared' },
] as const;

export const reactorEventTypeOptions = [
  { value: 'inoculation', label: 'Inokulation' },
  { value: 'medium_change', label: 'Mediumwechsel' },
  { value: 'calibration', label: 'Kalibrierung' },
  { value: 'contamination_suspected', label: 'Kontaminationsverdacht' },
  { value: 'contamination_confirmed', label: 'Kontamination bestaetigt' },
  { value: 'maintenance', label: 'Wartung' },
  { value: 'manual_adjustment', label: 'Manuelle Anpassung' },
  { value: 'observation', label: 'Beobachtung' },
  { value: 'harvest', label: 'Ernte' },
  { value: 'incident', label: 'Incident' },
] as const;

export const assetTypeOptions = [
  { value: 'printer_3d', label: '3D-Drucker' },
  { value: 'microscope', label: 'Mikroskop' },
  { value: 'soldering_station', label: 'Loetstation' },
  { value: 'power_supply', label: 'Netzteil' },
  { value: 'pump', label: 'Pumpe' },
  { value: 'server', label: 'Server' },
  { value: 'gpu_node', label: 'GPU-Node' },
  { value: 'sbc', label: 'SBC' },
  { value: 'network_device', label: 'Netzwerkgeraet' },
  { value: 'lab_device', label: 'Laborgeraet' },
  { value: 'tool', label: 'Tool' },
] as const;

export const assetStatusOptions = [
  { value: 'active', label: 'Aktiv' },
  { value: 'maintenance', label: 'Wartung' },
  { value: 'error', label: 'Fehler' },
  { value: 'inactive', label: 'Inaktiv' },
  { value: 'retired', label: 'Ausgemustert' },
] as const;

export const inventoryCategoryOptions = [
  { value: 'filament', label: 'Filament' },
  { value: 'electronic_component', label: 'Elektronikteil' },
  { value: 'cable', label: 'Kabel' },
  { value: 'screw', label: 'Schrauben' },
  { value: 'tubing', label: 'Schlauch / Tubing' },
  { value: 'chemical', label: 'Chemikalie' },
  { value: 'nutrient', label: 'Naehrmedium' },
  { value: 'cleaning_supply', label: 'Reinigungsmittel' },
  { value: 'spare_part', label: 'Ersatzteil' },
  { value: 'consumable', label: 'Verbrauchsmaterial' },
  { value: 'storage_box_content', label: 'Boxinhalt' },
] as const;

export const inventoryStatusOptions = [
  { value: 'available', label: 'Verfuegbar' },
  { value: 'low_stock', label: 'Knapp' },
  { value: 'out_of_stock', label: 'Leer' },
  { value: 'reserved', label: 'Reserviert' },
  { value: 'expired', label: 'Abgelaufen' },
  { value: 'archived', label: 'Archiviert' },
] as const;

export const labelTypeOptions = [
  { value: 'qr', label: 'QR' },
  { value: 'printed_label', label: 'Gedrucktes Label' },
] as const;

export const labelTargetTypeOptions = [
  { value: 'asset', label: 'Asset' },
  { value: 'inventory_item', label: 'Inventory' },
] as const;

export const userRoleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'operator', label: 'Operator' },
  { value: 'viewer', label: 'Viewer' },
] as const;

export const sensorTypeOptions = [
  { value: 'temperature', label: 'Temperatur' },
  { value: 'humidity', label: 'Luftfeuchte' },
  { value: 'water_temperature', label: 'Wassertemperatur' },
  { value: 'ph', label: 'pH' },
  { value: 'ec', label: 'EC' },
  { value: 'light', label: 'Licht' },
  { value: 'co2', label: 'CO2' },
] as const;

export const sensorStatusOptions = [
  { value: 'active', label: 'Aktiv' },
  { value: 'inactive', label: 'Inaktiv' },
  { value: 'error', label: 'Fehler' },
  { value: 'maintenance', label: 'Wartung' },
] as const;

export const taskStatusOptions = [
  { value: 'open', label: 'Offen' },
  { value: 'doing', label: 'In Arbeit' },
  { value: 'blocked', label: 'Blockiert' },
  { value: 'done', label: 'Erledigt' },
] as const;

export const taskPriorityOptions = [
  { value: 'low', label: 'Niedrig' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'Hoch' },
  { value: 'critical', label: 'Kritisch' },
] as const;

export const alertSeverityOptions = [
  { value: 'info', label: 'Info' },
  { value: 'warning', label: 'Warnung' },
  { value: 'high', label: 'Hoch' },
  { value: 'critical', label: 'Kritisch' },
] as const;

export const alertStatusOptions = [
  { value: 'open', label: 'Offen' },
  { value: 'acknowledged', label: 'Quittiert' },
  { value: 'resolved', label: 'Geloest' },
] as const;

export const alertSourceTypeOptions = [
  { value: 'manual', label: 'Manuell' },
  { value: 'sensor', label: 'Sensor' },
  { value: 'charge', label: 'Charge' },
  { value: 'reactor', label: 'Reaktor' },
  { value: 'system', label: 'System' },
] as const;

export const abrainPresetOptions = [
  { value: 'daily_overview', label: 'Tagesueberblick' },
  { value: 'critical_issues', label: 'Kritische Themen' },
  { value: 'overdue_tasks', label: 'Ueberfaellige Aufgaben' },
  { value: 'sensor_attention', label: 'Sensor Aufmerksamkeit' },
  { value: 'reactor_attention', label: 'Reaktor Aufmerksamkeit' },
  { value: 'recent_activity', label: 'Letzte Aktivitaet' },
] as const;

export const abrainContextSectionOptions = [
  { value: 'tasks', label: 'Tasks' },
  { value: 'alerts', label: 'Alerts' },
  { value: 'sensors', label: 'Sensoren' },
  { value: 'charges', label: 'Charges' },
  { value: 'reactors', label: 'Reaktoren' },
  { value: 'photos', label: 'Fotos' },
] as const;

export const ruleTriggerTypeOptions = [
  { value: 'sensor_threshold', label: 'Sensor Threshold' },
  { value: 'stale_sensor', label: 'Stale Sensor' },
  { value: 'overdue_tasks', label: 'Overdue Tasks' },
  { value: 'reactor_status', label: 'Reactor Status' },
] as const;

export const ruleConditionTypeOptions = [
  { value: 'threshold_gt', label: 'Threshold >' },
  { value: 'threshold_lt', label: 'Threshold <' },
  { value: 'age_gt_hours', label: 'Age > Hours' },
  { value: 'count_gt', label: 'Count >' },
  { value: 'status_is', label: 'Status Is' },
] as const;

export const ruleActionTypeOptions = [
  { value: 'create_alert', label: 'Alert erzeugen' },
  { value: 'create_task', label: 'Task erzeugen' },
] as const;

export const ruleExecutionStatusOptions = [
  { value: 'matched', label: 'Matched' },
  { value: 'not_matched', label: 'Not Matched' },
  { value: 'executed', label: 'Executed' },
  { value: 'failed', label: 'Failed' },
] as const;

export type ChargeStatus = (typeof chargeStatusOptions)[number]['value'];
export type ReactorStatus = (typeof reactorStatusOptions)[number]['value'];
export type ReactorPhase = (typeof reactorPhaseOptions)[number]['value'];
export type ReactorTechnicalState = (typeof reactorTechnicalStateOptions)[number]['value'];
export type ReactorBiologicalState = (typeof reactorBiologicalStateOptions)[number]['value'];
export type ReactorContaminationState = (typeof reactorContaminationStateOptions)[number]['value'];
export type ReactorEventType = (typeof reactorEventTypeOptions)[number]['value'];
export type AssetType = (typeof assetTypeOptions)[number]['value'];
export type AssetStatus = (typeof assetStatusOptions)[number]['value'];
export type InventoryCategory = (typeof inventoryCategoryOptions)[number]['value'];
export type InventoryStatus = (typeof inventoryStatusOptions)[number]['value'];
export type LabelType = (typeof labelTypeOptions)[number]['value'];
export type LabelTargetType = (typeof labelTargetTypeOptions)[number]['value'];
export type UserRole = (typeof userRoleOptions)[number]['value'];
export type SensorType = (typeof sensorTypeOptions)[number]['value'];
export type SensorStatus = (typeof sensorStatusOptions)[number]['value'];
export type TaskStatus = (typeof taskStatusOptions)[number]['value'];
export type TaskPriority = (typeof taskPriorityOptions)[number]['value'];
export type AlertSeverity = (typeof alertSeverityOptions)[number]['value'];
export type AlertStatus = (typeof alertStatusOptions)[number]['value'];
export type AlertSourceType = (typeof alertSourceTypeOptions)[number]['value'];
export type ABrainPreset = (typeof abrainPresetOptions)[number]['value'];
export type ABrainContextSection = (typeof abrainContextSectionOptions)[number]['value'];
export type RuleTriggerType = (typeof ruleTriggerTypeOptions)[number]['value'];
export type RuleConditionType = (typeof ruleConditionTypeOptions)[number]['value'];
export type RuleActionType = (typeof ruleActionTypeOptions)[number]['value'];
export type RuleExecutionStatus = (typeof ruleExecutionStatusOptions)[number]['value'];

export type Charge = {
  id: number;
  name: string;
  species: string;
  status: ChargeStatus;
  volume_l: number;
  reactor_id: number | null;
  start_date: string;
  notes: string | null;
};

export type Reactor = {
  id: number;
  name: string;
  reactor_type: string;
  status: ReactorStatus;
  volume_l: number;
  location: string | null;
  last_cleaned_at: string | null;
  notes: string | null;
};

export type ReactorEvent = {
  id: number;
  reactor_id: number;
  reactor_name: string | null;
  event_type: ReactorEventType;
  title: string;
  description: string | null;
  severity: AlertSeverity | null;
  phase_snapshot: ReactorPhase | null;
  created_at: string;
  created_by_user_id: number | null;
  created_by_username: string | null;
};

export type ReactorTwin = {
  id: number | null;
  is_configured: boolean;
  reactor_id: number;
  reactor_name: string;
  reactor_type: string;
  reactor_status: ReactorStatus;
  reactor_volume_l: number;
  reactor_location: string | null;
  culture_type: string | null;
  strain: string | null;
  medium_recipe: string | null;
  inoculated_at: string | null;
  current_phase: ReactorPhase;
  target_ph_min: number | null;
  target_ph_max: number | null;
  target_temp_min: number | null;
  target_temp_max: number | null;
  target_light_min: number | null;
  target_light_max: number | null;
  target_flow_min: number | null;
  target_flow_max: number | null;
  expected_harvest_window_start: string | null;
  expected_harvest_window_end: string | null;
  contamination_state: ReactorContaminationState | null;
  technical_state: ReactorTechnicalState;
  biological_state: ReactorBiologicalState;
  notes: string | null;
  created_at: string;
  updated_at: string;
  current_charge: Charge | null;
  sensor_count: number;
  open_task_count: number;
  open_alert_count: number;
  photo_count: number;
  latest_event: ReactorEvent | null;
};

export type ReactorTwinDetail = ReactorTwin & {
  recent_events: ReactorEvent[];
  open_tasks: Task[];
  recent_alerts: Alert[];
  recent_photos: Photo[];
  recent_sensors: Sensor[];
};

export type Asset = {
  id: number;
  name: string;
  asset_type: AssetType;
  category: string;
  status: AssetStatus;
  location: string;
  zone: string | null;
  serial_number: string | null;
  manufacturer: string | null;
  model: string | null;
  notes: string | null;
  maintenance_notes: string | null;
  last_maintenance_at: string | null;
  next_maintenance_at: string | null;
  wiki_ref: string | null;
  created_at: string;
  updated_at: string;
  open_task_count: number;
  photo_count: number;
};

export type InventoryItem = {
  id: number;
  name: string;
  category: string;
  status: InventoryStatus;
  quantity: number;
  unit: string;
  min_quantity: number | null;
  location: string;
  zone: string | null;
  supplier: string | null;
  sku: string | null;
  notes: string | null;
  asset_id: number | null;
  asset_name: string | null;
  wiki_ref: string | null;
  last_restocked_at: string | null;
  expiry_date: string | null;
  created_at: string;
  updated_at: string;
  is_low_stock: boolean;
  is_out_of_stock: boolean;
  needs_restock: boolean;
};

export type Sensor = {
  id: number;
  name: string;
  sensor_type: SensorType;
  unit: string;
  status: SensorStatus;
  reactor_id: number | null;
  location: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  reactor_name: string | null;
  last_value: number | null;
  last_recorded_at: string | null;
  last_value_source: string | null;
};

export type SensorValue = {
  id: number;
  sensor_id: number;
  value: number;
  source: string | null;
  recorded_at: string;
};

export type Task = {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_at: string | null;
  charge_id: number | null;
  reactor_id: number | null;
  asset_id: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
  asset_name: string | null;
};

export type Alert = {
  id: number;
  title: string;
  message: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source_type: AlertSourceType;
  source_id: number | null;
  created_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
};

export type Photo = {
  id: number;
  filename: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  storage_path: string;
  title: string | null;
  notes: string | null;
  charge_id: number | null;
  reactor_id: number | null;
  asset_id: number | null;
  created_at: string;
  uploaded_by: string | null;
  captured_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
  asset_name: string | null;
  file_url: string;
};

export type AssetDetail = Asset & {
  open_tasks: Task[];
  recent_photos: Photo[];
};

export type AssetOverview = {
  active_assets: number;
  assets_in_maintenance: number;
  assets_in_error: number;
  upcoming_maintenance_assets: Asset[];
};

export type InventoryOverview = {
  total_items: number;
  low_stock_items: number;
  out_of_stock_items: number;
  critical_items: InventoryItem[];
};

export type Label = {
  id: number;
  label_code: string;
  label_type: LabelType;
  target_type: LabelTargetType;
  target_id: number;
  display_name: string | null;
  location_snapshot: string | null;
  note: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  target_name: string | null;
  target_location: string | null;
  target_status: string | null;
  scan_path: string;
  scan_url: string;
  target_manager_path: string;
  target_manager_url: string;
  qr_path: string;
  qr_url: string;
};

export type LabelTarget = {
  label: Label;
  asset: Asset | null;
  inventory_item: InventoryItem | null;
};

export type LabelOverview = {
  labeled_assets: number;
  labeled_inventory_items: number;
  recent_labels: Label[];
};

export type User = {
  id: number;
  username: string;
  display_name: string | null;
  email: string | null;
  role: UserRole;
  is_active: boolean;
  auth_source: string;
  note: string | null;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
};

export type AuthLoginResponse = {
  access_token: string;
  user: User;
};

export type PhotoAnalysisStatus = {
  photo_id: number;
  status: string;
  detail: string;
};

export type ABrainStatus = {
  connected: boolean;
  mode: string;
  base_url: string;
  timeout_seconds: number;
  fallback_available: boolean;
  note: string;
};

export type ABrainPresetDefinition = {
  id: ABrainPreset;
  title: string;
  description: string;
  default_question: string;
  default_sections: ABrainContextSection[];
};

export type ABrainReference = {
  entity_type: string;
  entity_id: number;
  label: string;
};

export type ABrainSummaryCounts = {
  open_tasks: number;
  overdue_tasks: number;
  due_today_tasks: number;
  critical_alerts: number;
  open_alerts: number;
  sensor_attention: number;
  active_charges: number;
  reactors_online: number;
  recent_photos: number;
};

export type ABrainTaskContextItem = {
  id: number;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
};

export type ABrainAlertContextItem = {
  id: number;
  title: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source_type: AlertSourceType;
  created_at: string;
};

export type ABrainSensorAttentionItem = {
  id: number;
  name: string;
  status: SensorStatus;
  reactor_name: string | null;
  last_recorded_at: string | null;
  last_value: number | null;
  attention_reason: string;
};

export type ABrainChargeContextItem = {
  id: number;
  name: string;
  species: string;
  status: ChargeStatus;
};

export type ABrainReactorContextItem = {
  id: number;
  name: string;
  status: ReactorStatus;
  open_task_count: number;
};

export type ABrainPhotoContextItem = {
  id: number;
  title: string | null;
  created_at: string;
  captured_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
};

export type ABrainContext = {
  generated_at: string;
  included_sections: ABrainContextSection[];
  summary: ABrainSummaryCounts;
  tasks: ABrainTaskContextItem[] | null;
  alerts: ABrainAlertContextItem[] | null;
  sensors: ABrainSensorAttentionItem[] | null;
  charges: ABrainChargeContextItem[] | null;
  reactors: ABrainReactorContextItem[] | null;
  photos: ABrainPhotoContextItem[] | null;
};

export type ABrainQueryResponse = {
  question: string;
  preset: ABrainPreset | null;
  mode: string;
  fallback_used: boolean;
  summary: string;
  highlights: string[];
  recommended_actions: string[];
  referenced_entities: ABrainReference[];
  used_context_sections: ABrainContextSection[];
  note: string | null;
};

export type Rule = {
  id: number;
  name: string;
  description: string | null;
  is_enabled: boolean;
  trigger_type: RuleTriggerType;
  condition_type: RuleConditionType;
  condition_config: Record<string, unknown>;
  action_type: RuleActionType;
  action_config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  last_evaluated_at: string | null;
};

export type RuleExecution = {
  id: number;
  rule_id: number;
  rule_name: string | null;
  status: RuleExecutionStatus;
  dry_run: boolean;
  evaluation_summary: Record<string, unknown>;
  action_result: Record<string, unknown>;
  created_at: string;
};

export type RuleEvaluationResponse = {
  rule: Rule;
  execution: RuleExecution;
};

export type DashboardSummary = {
  active_charges: number;
  reactors_online: number;
  reactors_attention: number;
  reactors_harvest_ready: number;
  reactors_incident_or_contamination: number;
  active_sensors: number;
  error_sensors: number;
  active_assets: number;
  assets_in_maintenance: number;
  assets_in_error: number;
  labeled_assets: number;
  inventory_items: number;
  inventory_low_stock: number;
  inventory_out_of_stock: number;
  labeled_inventory_items: number;
  open_tasks: number;
  due_today_tasks: number;
  critical_alerts: number;
  open_alerts: number;
  photo_count: number;
  uploads_last_7_days: number;
  active_rules: number;
  sensor_overview: Sensor[];
  recent_alerts: Alert[];
  recent_photos: Photo[];
  recent_reactor_events: ReactorEvent[];
  recent_rule_executions: RuleExecution[];
  upcoming_maintenance_assets: Asset[];
  critical_inventory_items: InventoryItem[];
  recent_labels: Label[];
  message: string;
};
