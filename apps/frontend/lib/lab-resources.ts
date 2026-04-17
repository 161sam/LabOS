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

export type ChargeStatus = (typeof chargeStatusOptions)[number]['value'];
export type ReactorStatus = (typeof reactorStatusOptions)[number]['value'];

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
