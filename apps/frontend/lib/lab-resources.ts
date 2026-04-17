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

export type ChargeStatus = (typeof chargeStatusOptions)[number]['value'];
export type ReactorStatus = (typeof reactorStatusOptions)[number]['value'];
export type SensorType = (typeof sensorTypeOptions)[number]['value'];
export type SensorStatus = (typeof sensorStatusOptions)[number]['value'];

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

export type DashboardSummary = {
  active_charges: number;
  reactors_online: number;
  open_alerts: number;
  today_tasks: number;
  active_sensors: number;
  error_sensors: number;
  sensor_overview: Sensor[];
  message: string;
};
