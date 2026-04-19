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

export const telemetrySensorTypeOptions = [
  { value: 'temp', label: 'Temperatur' },
  { value: 'ph', label: 'pH' },
  { value: 'light', label: 'Licht' },
  { value: 'flow', label: 'Flow' },
  { value: 'ec', label: 'EC' },
  { value: 'co2', label: 'CO2' },
  { value: 'humidity', label: 'Luftfeuchte' },
] as const;

export const telemetrySourceOptions = [
  { value: 'manual', label: 'Manual' },
  { value: 'device', label: 'Device' },
  { value: 'simulated', label: 'Simulated' },
] as const;

export const deviceNodeTypeOptions = [
  { value: 'sampling', label: 'Sampling' },
  { value: 'env_control', label: 'Env Control' },
  { value: 'sensor_bridge', label: 'Sensor Bridge' },
  { value: 'pump_driver', label: 'Pump Driver' },
  { value: 'light_controller', label: 'Light Controller' },
  { value: 'dosing', label: 'Dosing' },
  { value: 'safety', label: 'Safety' },
  { value: 'vision', label: 'Vision' },
] as const;

export const deviceNodeStatusOptions = [
  { value: 'online', label: 'Online' },
  { value: 'offline', label: 'Offline' },
  { value: 'warning', label: 'Warning' },
  { value: 'error', label: 'Error' },
] as const;

export const reactorControlParameterOptions = [
  { value: 'temp', label: 'Temperatur' },
  { value: 'ph', label: 'pH' },
  { value: 'light', label: 'Licht' },
  { value: 'flow', label: 'Flow' },
  { value: 'ec', label: 'EC' },
  { value: 'co2', label: 'CO2' },
  { value: 'humidity', label: 'Luftfeuchte' },
] as const;

export const reactorSetpointModeOptions = [
  { value: 'auto', label: 'Auto' },
  { value: 'manual', label: 'Manual' },
] as const;

export const reactorCommandTypeOptions = [
  { value: 'light_on', label: 'Light On' },
  { value: 'light_off', label: 'Light Off' },
  { value: 'pump_on', label: 'Pump On' },
  { value: 'pump_off', label: 'Pump Off' },
  { value: 'aeration_start', label: 'Aeration Start' },
  { value: 'aeration_stop', label: 'Aeration Stop' },
  { value: 'sample_capture', label: 'Sample Capture' },
] as const;

export const reactorCommandStatusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'sent', label: 'Sent' },
  { value: 'acknowledged', label: 'Bestätigt' },
  { value: 'failed', label: 'Failed' },
  { value: 'blocked', label: 'Blockiert' },
  { value: 'timeout', label: 'Timeout' },
  { value: 'retrying', label: 'Retry läuft' },
] as const;

export const calibrationTargetTypeOptions = [
  { value: 'reactor', label: 'Reaktor' },
  { value: 'device_node', label: 'Device Node' },
  { value: 'asset', label: 'Asset' },
] as const;

export const calibrationStatusOptions = [
  { value: 'valid', label: 'Gueltig' },
  { value: 'due', label: 'Faellig' },
  { value: 'expired', label: 'Abgelaufen' },
  { value: 'failed', label: 'Fehlgeschlagen' },
  { value: 'unknown', label: 'Unbekannt' },
] as const;

export const maintenanceTargetTypeOptions = [
  { value: 'reactor', label: 'Reaktor' },
  { value: 'device_node', label: 'Device Node' },
  { value: 'asset', label: 'Asset' },
] as const;

export const maintenanceTypeOptions = [
  { value: 'cleaning', label: 'Reinigung' },
  { value: 'inspection', label: 'Inspektion' },
  { value: 'replacement', label: 'Austausch' },
  { value: 'tubing_flush', label: 'Schlauchspuelung' },
  { value: 'filter_change', label: 'Filterwechsel' },
  { value: 'pump_service', label: 'Pumpenservice' },
  { value: 'general_service', label: 'Allgemeiner Service' },
] as const;

export const maintenanceStatusOptions = [
  { value: 'scheduled', label: 'Geplant' },
  { value: 'done', label: 'Erledigt' },
  { value: 'overdue', label: 'Ueberfaellig' },
  { value: 'skipped', label: 'Uebersprungen' },
] as const;

export const incidentTypeOptions = [
  { value: 'sensor_untrusted', label: 'Sensor nicht vertrauenswuerdig' },
  { value: 'calibration_expired', label: 'Kalibrierung abgelaufen' },
  { value: 'node_offline', label: 'Node offline' },
  { value: 'overheating_risk', label: 'Ueberhitzungsrisiko' },
  { value: 'dry_run_risk', label: 'Trockenlaufrisiko' },
  { value: 'clogging_suspected', label: 'Verstopfungsverdacht' },
  { value: 'flow_mismatch', label: 'Flow-Abweichung' },
  { value: 'invalid_telemetry', label: 'Ungueltige Telemetrie' },
  { value: 'unsafe_command_blocked', label: 'Unsicherer Befehl blockiert' },
  { value: 'general', label: 'Allgemein' },
] as const;

export const incidentSeverityOptions = [
  { value: 'info', label: 'Info' },
  { value: 'warning', label: 'Warnung' },
  { value: 'high', label: 'Hoch' },
  { value: 'critical', label: 'Kritisch' },
] as const;

export const incidentStatusOptions = [
  { value: 'open', label: 'Offen' },
  { value: 'acknowledged', label: 'Quittiert' },
  { value: 'resolved', label: 'Geloest' },
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

export const reactorHealthStatusOptions = [
  { value: 'nominal', label: 'Nominal' },
  { value: 'attention', label: 'Auffaellig' },
  { value: 'warning', label: 'Warnung' },
  { value: 'incident', label: 'Incident' },
  { value: 'unknown', label: 'Unbekannt' },
] as const;

export const reactorHealthSignalSeverityOptions = [
  { value: 'info', label: 'Info' },
  { value: 'attention', label: 'Auffaellig' },
  { value: 'warning', label: 'Warnung' },
  { value: 'incident', label: 'Incident' },
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
export type TelemetrySensorType = (typeof telemetrySensorTypeOptions)[number]['value'];
export type TelemetrySource = (typeof telemetrySourceOptions)[number]['value'];
export type DeviceNodeType = (typeof deviceNodeTypeOptions)[number]['value'];
export type DeviceNodeStatus = (typeof deviceNodeStatusOptions)[number]['value'];
export type ReactorControlParameter = (typeof reactorControlParameterOptions)[number]['value'];
export type ReactorSetpointMode = (typeof reactorSetpointModeOptions)[number]['value'];
export type ReactorCommandType = (typeof reactorCommandTypeOptions)[number]['value'];
export type ReactorCommandStatus = (typeof reactorCommandStatusOptions)[number]['value'];
export type CalibrationTargetType = (typeof calibrationTargetTypeOptions)[number]['value'];
export type CalibrationStatus = (typeof calibrationStatusOptions)[number]['value'];
export type MaintenanceTargetType = (typeof maintenanceTargetTypeOptions)[number]['value'];
export type MaintenanceType = (typeof maintenanceTypeOptions)[number]['value'];
export type MaintenanceStatus = (typeof maintenanceStatusOptions)[number]['value'];
export type IncidentType = (typeof incidentTypeOptions)[number]['value'];
export type IncidentSeverity = (typeof incidentSeverityOptions)[number]['value'];
export type IncidentStatus = (typeof incidentStatusOptions)[number]['value'];
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
export type ReactorHealthStatus = (typeof reactorHealthStatusOptions)[number]['value'];
export type ReactorHealthSignalSeverity = (typeof reactorHealthSignalSeverityOptions)[number]['value'];

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

export type TelemetryValue = {
  id: number;
  reactor_id: number;
  reactor_name: string | null;
  sensor_type: TelemetrySensorType;
  value: number;
  unit: string;
  source: TelemetrySource;
  timestamp: string;
  created_at: string;
};

export type DeviceNode = {
  id: number;
  name: string;
  node_id: string | null;
  node_type: DeviceNodeType;
  status: DeviceNodeStatus;
  last_seen_at: string;
  firmware_version: string | null;
  reactor_id: number | null;
  reactor_name: string | null;
  created_at: string;
  updated_at: string;
};

export type ReactorSetpoint = {
  id: number;
  reactor_id: number;
  reactor_name: string | null;
  parameter: ReactorControlParameter;
  target_value: number;
  min_value: number | null;
  max_value: number | null;
  mode: ReactorSetpointMode;
  updated_at: string;
};

export type ReactorCommand = {
  id: number;
  reactor_id: number;
  reactor_name: string | null;
  command_type: ReactorCommandType;
  status: ReactorCommandStatus;
  blocked_reason: string | null;
  command_uid: string;
  published_at: string | null;
  acknowledged_at: string | null;
  retry_count: number;
  max_retries: number;
  last_error: string | null;
  timeout_at: string | null;
  ack_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type CalibrationRecord = {
  id: number;
  target_type: CalibrationTargetType;
  target_id: number;
  target_name: string | null;
  parameter: string;
  status: CalibrationStatus;
  calibrated_at: string | null;
  due_at: string | null;
  calibration_value: number | null;
  reference_value: number | null;
  performed_by_user_id: number | null;
  performed_by_username: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
};

export type CalibrationOverview = {
  total: number;
  valid: number;
  due: number;
  expired: number;
  failed: number;
  unknown: number;
  due_or_expired: number;
};

export type MaintenanceRecord = {
  id: number;
  target_type: MaintenanceTargetType;
  target_id: number;
  target_name: string | null;
  maintenance_type: MaintenanceType;
  status: MaintenanceStatus;
  performed_at: string | null;
  due_at: string | null;
  performed_by_user_id: number | null;
  performed_by_username: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
};

export type MaintenanceOverview = {
  total: number;
  scheduled: number;
  done: number;
  overdue: number;
  skipped: number;
};

export type SafetyIncident = {
  id: number;
  reactor_id: number | null;
  reactor_name: string | null;
  device_node_id: number | null;
  device_node_name: string | null;
  asset_id: number | null;
  incident_type: IncidentType;
  severity: IncidentSeverity;
  status: IncidentStatus;
  title: string;
  description: string | null;
  created_at: string;
  resolved_at: string | null;
  created_by_user_id: number | null;
  created_by_username: string | null;
};

export type SafetyOverview = {
  open_incidents: number;
  acknowledged_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  blocked_commands: number;
  calibration_expired: number;
  maintenance_overdue: number;
};

export type MQTTBridgeStatus = {
  enabled: boolean;
  dependency_available: boolean;
  connected: boolean;
  broker_host: string;
  broker_port: number;
  client_id: string;
  topic_prefix: string;
  publish_commands: boolean;
  last_message_at: string | null;
  last_error: string | null;
};

export type ReactorHealthSignal = {
  code: string;
  severity: ReactorHealthSignalSeverity;
  source: string;
  message: string;
};

export type ReactorHealthAssessment = {
  id: number;
  reactor_id: number;
  reactor_name: string | null;
  status: ReactorHealthStatus;
  summary: string;
  signals: ReactorHealthSignal[];
  source_telemetry_at: string | null;
  source_vision_analysis_id: number | null;
  source_incident_count: number;
  assessed_at: string;
  created_at: string;
};

export const reactorHealthStatusLabels: Record<ReactorHealthStatus, string> = {
  nominal: 'Nominal',
  attention: 'Auffaellig',
  warning: 'Warnung',
  incident: 'Incident',
  unknown: 'Unbekannt',
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
  latest_health: ReactorHealthAssessment | null;
};

export type ReactorTwinDetail = ReactorTwin & {
  recent_events: ReactorEvent[];
  open_tasks: Task[];
  recent_alerts: Alert[];
  recent_photos: Photo[];
  recent_sensors: Sensor[];
};

export type ReactorTelemetryOverview = {
  reactor_id: number;
  reactor_name: string;
  latest_temp: number | null;
  latest_temp_unit: string | null;
  latest_ph: number | null;
  latest_ph_unit: string | null;
  last_telemetry_at: string | null;
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

export type VisionAnalysisResult = {
  width?: number;
  height?: number;
  avg_rgb?: [number, number, number];
  rgb_stddev?: [number, number, number];
  brightness?: number;
  sharpness?: number;
  dominant_rgb?: [number, number, number];
  dominant_ratio?: number;
  green_ratio?: number;
  brown_ratio?: number;
  health_label?: string;
  confidence?: number;
};

export type VisionAnalysis = {
  id: number;
  photo_id: number;
  reactor_id: number | null;
  analysis_type: string;
  status: string;
  result: VisionAnalysisResult;
  confidence: number | null;
  error: string | null;
  created_at: string;
};

export const visionHealthLabels: Record<string, string> = {
  healthy_green: 'Grün / gesund',
  growing: 'Wächst',
  low_biomass: 'Wenig Biomasse',
  no_growth_visible: 'Kein Wachstum sichtbar',
  contamination_suspected: 'Kontamination verdächtig',
  too_dark: 'Zu dunkel',
  overexposed: 'Überbelichtet',
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
  latest_vision: VisionAnalysis | null;
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
  latest_vision: VisionAnalysis | null;
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
  health_status: ReactorHealthStatus | null;
  health_summary: string | null;
  health_assessed_at: string | null;
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

export type ABrainActionRiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type ABrainActionDomain =
  | 'operations'
  | 'reactor'
  | 'safety'
  | 'maintenance'
  | 'vision'
  | 'scheduler';

export type ABrainActionDescriptor = {
  name: string;
  description: string;
  domain: ABrainActionDomain;
  risk_level: ABrainActionRiskLevel;
  requires_approval: boolean;
  allowed_roles: string[];
  arguments: Record<string, string>;
  guarded_by: string[];
  notes: string | null;
};

export type ABrainActionCatalog = {
  contract_version: string;
  generated_at: string;
  actions: ABrainActionDescriptor[];
};

export type ABrainAdapterTelemetrySummary = {
  sensor_type: string;
  latest_value: number | null;
  unit: string | null;
  last_at: string | null;
  in_range: boolean | null;
};

export type ABrainAdapterReactorContext = {
  id: number;
  name: string;
  status: ReactorStatus;
  phase: ReactorPhase | null;
  technical_state: ReactorTechnicalState | null;
  biological_state: ReactorBiologicalState | null;
  health_status: ReactorHealthStatus | null;
  health_summary: string | null;
  health_assessed_at: string | null;
  open_task_count: number;
  open_incident_count: number;
  telemetry: ABrainAdapterTelemetrySummary[];
  latest_vision_label: string | null;
  latest_vision_confidence: number | null;
};

export type ABrainAdapterOperationsContext = {
  overdue_tasks: ABrainTaskContextItem[];
  critical_alerts: ABrainAlertContextItem[];
  blocked_command_count: number;
  failed_command_count: number;
  due_calibration_count: number;
  overdue_maintenance_count: number;
  open_safety_incident_count: number;
};

export type ABrainAdapterResourceContextItem = {
  kind: string;
  id: number;
  name: string;
  detail: string | null;
};

export type ABrainAdapterResourceContext = {
  low_stock: ABrainAdapterResourceContextItem[];
  out_of_stock: ABrainAdapterResourceContextItem[];
  assets_attention: ABrainAdapterResourceContextItem[];
  offline_nodes: ABrainAdapterResourceContextItem[];
};

export type ABrainAdapterScheduleContext = {
  active_schedule_count: number;
  recent_failed_run_count: number;
  schedules: ABrainAdapterResourceContextItem[];
};

export type ABrainAdapterContext = {
  generated_at: string;
  contract_version: string;
  mode: string;
  fallback_used: boolean;
  summary: ABrainSummaryCounts;
  reactors: ABrainAdapterReactorContext[];
  operations: ABrainAdapterOperationsContext;
  resources: ABrainAdapterResourceContext;
  schedule: ABrainAdapterScheduleContext;
  photos: ABrainPhotoContextItem[];
};

export type ABrainAdapterRecommendedAction = {
  action: string;
  target: string | null;
  reason: string;
  risk_level: ABrainActionRiskLevel;
  requires_approval: boolean;
  blocked: boolean;
  blocked_reason: string | null;
};

export type ABrainAdapterResponse = {
  question: string;
  preset: ABrainPreset | null;
  mode: string;
  fallback_used: boolean;
  contract_version: string;
  trace_id: string | null;
  summary: string;
  highlights: string[];
  recommended_actions: ABrainAdapterRecommendedAction[];
  blocked_actions: ABrainAdapterRecommendedAction[];
  approval_required: boolean;
  policy_decision: string | null;
  used_context_sections: ABrainContextSection[];
  referenced_entities: ABrainReference[];
  notes: string[];
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

export const scheduleTypeOptions = [
  { value: 'interval', label: 'Interval' },
  { value: 'cron', label: 'Cron' },
  { value: 'manual', label: 'Manuell' },
] as const;

export const scheduleTargetTypeOptions = [
  { value: 'command', label: 'Reactor Command' },
  { value: 'rule', label: 'Rule' },
] as const;

export const scheduleExecutionStatusOptions = [
  { value: 'success', label: 'Success' },
  { value: 'failed', label: 'Failed' },
  { value: 'skipped', label: 'Skipped' },
] as const;

export type ScheduleType = (typeof scheduleTypeOptions)[number]['value'];
export type ScheduleTargetType = (typeof scheduleTargetTypeOptions)[number]['value'];
export type ScheduleExecutionStatus = (typeof scheduleExecutionStatusOptions)[number]['value'];

export type Schedule = {
  id: number;
  name: string;
  description: string | null;
  schedule_type: ScheduleType;
  interval_seconds: number | null;
  cron_expr: string | null;
  target_type: ScheduleTargetType;
  target_id: number | null;
  reactor_id: number | null;
  target_params: Record<string, unknown>;
  is_enabled: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  last_status: ScheduleExecutionStatus | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
};

export type ScheduleExecution = {
  id: number;
  schedule_id: number;
  status: ScheduleExecutionStatus;
  trigger: string;
  started_at: string;
  finished_at: string | null;
  result: Record<string, unknown>;
  error: string | null;
};

export type ScheduleRunResponse = {
  schedule: Schedule;
  execution: ScheduleExecution;
};

export type DashboardSummary = {
  active_charges: number;
  reactors_online: number;
  reactors_attention: number;
  reactors_harvest_ready: number;
  reactors_incident_or_contamination: number;
  reactors_health_nominal: number;
  reactors_health_attention: number;
  reactors_health_warning: number;
  reactors_health_incident: number;
  reactors_health_unknown: number;
  offline_devices: number;
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
  open_safety_incidents: number;
  calibration_due_or_expired: number;
  maintenance_overdue: number;
  sensor_overview: Sensor[];
  reactor_telemetry_overview: ReactorTelemetryOverview[];
  recent_alerts: Alert[];
  recent_photos: Photo[];
  recent_reactor_events: ReactorEvent[];
  recent_rule_executions: RuleExecution[];
  upcoming_maintenance_assets: Asset[];
  critical_inventory_items: InventoryItem[];
  recent_labels: Label[];
  recent_safety_incidents: SafetyIncident[];
  message: string;
};

export type ApprovalRequestStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'executed'
  | 'failed'
  | 'cancelled';

export type ApprovalRequestSource = 'abrain' | 'local_dev_fallback' | 'operator';

export type ApprovalRequestVia = 'adapter' | 'legacy_query' | 'future_mcp' | 'operator_ui';

export type ApprovalRequest = {
  id: number;
  action_name: string;
  action_params: Record<string, unknown>;
  requested_by_source: ApprovalRequestSource;
  requested_by_user_id: number | null;
  requested_by_username: string | null;
  requested_via: ApprovalRequestVia;
  trace_id: string | null;
  risk_level: ABrainActionRiskLevel | null;
  status: ApprovalRequestStatus;
  reason: string | null;
  decision_note: string | null;
  approval_required: boolean;
  approved_by_user_id: number | null;
  approved_by_username: string | null;
  decided_at: string | null;
  executed_execution_log_id: number | null;
  blocked_reason: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
};

export type ApprovalOverview = {
  pending: number;
  approved: number;
  rejected: number;
  executed: number;
  failed: number;
  cancelled: number;
  high_risk_pending: number;
};

export type TraceContextStatus = 'open' | 'completed' | 'failed';

export type TraceContextSource = 'abrain' | 'local' | 'operator' | 'api';

export type TraceContextSnapshot = {
  generated_at?: string | null;
  mode?: string | null;
  open_tasks?: number;
  overdue_tasks?: number;
  critical_alerts?: number;
  open_alerts?: number;
  open_safety_incidents?: number;
  blocked_commands?: number;
  failed_commands?: number;
  reactors?: Array<{
    id: number;
    name: string;
    status?: string | null;
    health_status?: string | null;
  }>;
  policy_decision?: string | null;
  approval_required?: boolean;
  [key: string]: unknown;
};

export type TraceContext = {
  trace_id: string;
  source: TraceContextSource;
  status: TraceContextStatus;
  root_query: string | null;
  summary: string | null;
  context_snapshot: TraceContextSnapshot;
  created_at: string;
  updated_at: string;
  execution_count: number;
  approval_count: number;
  pending_approval_count: number;
};

export type TraceTimelineEventKind = 'query' | 'approval' | 'execution';

export type TraceTimelineEvent = {
  kind: TraceTimelineEventKind;
  created_at: string;
  label: string;
  status: string | null;
  details: Record<string, unknown>;
};

export type ABrainExecutionLogEntry = {
  id: number;
  action: string;
  params: Record<string, unknown>;
  status: string;
  blocked_reason: string | null;
  source: string | null;
  executed_by: string | null;
  trace_id: string | null;
  result: Record<string, unknown>;
  created_at: string;
};

export type TraceContextDetail = TraceContext & {
  timeline: TraceTimelineEvent[];
  executions: ABrainExecutionLogEntry[];
  approvals: ApprovalRequest[];
};
