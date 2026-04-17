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

export type ChargeStatus = (typeof chargeStatusOptions)[number]['value'];
export type ReactorStatus = (typeof reactorStatusOptions)[number]['value'];
export type SensorType = (typeof sensorTypeOptions)[number]['value'];
export type SensorStatus = (typeof sensorStatusOptions)[number]['value'];
export type TaskStatus = (typeof taskStatusOptions)[number]['value'];
export type TaskPriority = (typeof taskPriorityOptions)[number]['value'];
export type AlertSeverity = (typeof alertSeverityOptions)[number]['value'];
export type AlertStatus = (typeof alertStatusOptions)[number]['value'];
export type AlertSourceType = (typeof alertSourceTypeOptions)[number]['value'];

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
  sensor_overview: Sensor[];
  recent_alerts: Alert[];
  recent_photos: Photo[];
  message: string;
};
