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
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
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
  created_at: string;
  uploaded_by: string | null;
  captured_at: string | null;
  charge_name: string | null;
  reactor_name: string | null;
  file_url: string;
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
  active_sensors: number;
  error_sensors: number;
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
  recent_rule_executions: RuleExecution[];
  message: string;
};
