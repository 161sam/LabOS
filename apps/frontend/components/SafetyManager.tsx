'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  CalibrationRecord,
  CalibrationStatus,
  CalibrationTargetType,
  IncidentSeverity,
  IncidentStatus,
  IncidentType,
  MaintenanceRecord,
  MaintenanceStatus,
  MaintenanceTargetType,
  MaintenanceType,
  SafetyIncident,
  SafetyOverview,
  calibrationStatusOptions,
  calibrationTargetTypeOptions,
  incidentSeverityOptions,
  incidentStatusOptions,
  incidentTypeOptions,
  maintenanceStatusOptions,
  maintenanceTargetTypeOptions,
  maintenanceTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type Tab = 'incidents' | 'calibration' | 'maintenance';

function getErrorMessage(error: unknown) {
  if (error instanceof Error) return error.message;
  return 'Unerwarteter Fehler';
}

function formatDateTime(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleString('de-DE');
}

function severityBadge(severity: string) {
  const map: Record<string, string> = {
    critical: 'badge-red',
    high: 'badge-orange',
    warning: 'badge-yellow',
    info: 'badge-blue',
  };
  return `badge ${map[severity] ?? 'badge-gray'}`;
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    open: 'badge-red',
    acknowledged: 'badge-yellow',
    resolved: 'badge-green',
    valid: 'badge-green',
    due: 'badge-yellow',
    expired: 'badge-red',
    failed: 'badge-red',
    unknown: 'badge-gray',
    scheduled: 'badge-blue',
    done: 'badge-green',
    overdue: 'badge-red',
    skipped: 'badge-gray',
  };
  return `badge ${map[status] ?? 'badge-gray'}`;
}

type IncidentForm = {
  reactor_id: string;
  device_node_id: string;
  incident_type: IncidentType;
  severity: IncidentSeverity;
  title: string;
  description: string;
};

type CalibrationForm = {
  target_type: CalibrationTargetType;
  target_id: string;
  parameter: string;
  status: CalibrationStatus;
  calibrated_at: string;
  due_at: string;
  calibration_value: string;
  reference_value: string;
  note: string;
};

type MaintenanceForm = {
  target_type: MaintenanceTargetType;
  target_id: string;
  maintenance_type: MaintenanceType;
  status: MaintenanceStatus;
  performed_at: string;
  due_at: string;
  note: string;
};

function emptyIncidentForm(): IncidentForm {
  return { reactor_id: '', device_node_id: '', incident_type: 'general', severity: 'warning', title: '', description: '' };
}

function emptyCalibrationForm(): CalibrationForm {
  return { target_type: 'reactor', target_id: '', parameter: '', status: 'unknown', calibrated_at: '', due_at: '', calibration_value: '', reference_value: '', note: '' };
}

function emptyMaintenanceForm(): MaintenanceForm {
  return { target_type: 'reactor', target_id: '', maintenance_type: 'cleaning', status: 'scheduled', performed_at: '', due_at: '', note: '' };
}

export function SafetyManager() {
  const [tab, setTab] = useState<Tab>('incidents');
  const [overview, setOverview] = useState<SafetyOverview | null>(null);
  const [incidents, setIncidents] = useState<SafetyIncident[]>([]);
  const [calibrations, setCalibrations] = useState<CalibrationRecord[]>([]);
  const [maintenances, setMaintenances] = useState<MaintenanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  const [incidentForm, setIncidentForm] = useState<IncidentForm>(emptyIncidentForm);
  const [showIncidentForm, setShowIncidentForm] = useState(false);
  const [calForm, setCalForm] = useState<CalibrationForm>(emptyCalibrationForm);
  const [showCalForm, setShowCalForm] = useState(false);
  const [maintForm, setMaintForm] = useState<MaintenanceForm>(emptyMaintenanceForm);
  const [showMaintForm, setShowMaintForm] = useState(false);

  const [incStatusFilter, setIncStatusFilter] = useState('');
  const [calStatusFilter, setCalStatusFilter] = useState('');
  const [maintStatusFilter, setMaintStatusFilter] = useState('');

  async function loadData() {
    setLoading(true);
    setPageError(null);
    try {
      const [ovData, incData, calData, maintData] = await Promise.all([
        apiRequest<SafetyOverview>('/api/v1/safety/overview'),
        apiRequest<SafetyIncident[]>('/api/v1/safety/incidents?limit=100'),
        apiRequest<CalibrationRecord[]>('/api/v1/calibration?limit=100'),
        apiRequest<MaintenanceRecord[]>('/api/v1/maintenance?limit=100'),
      ]);
      setOverview(ovData);
      setIncidents(incData);
      setCalibrations(calData);
      setMaintenances(maintData);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadData(); }, []);

  async function handleIncidentSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    const payload = {
      incident_type: incidentForm.incident_type,
      severity: incidentForm.severity,
      title: incidentForm.title,
      description: incidentForm.description || null,
      reactor_id: incidentForm.reactor_id ? Number(incidentForm.reactor_id) : null,
      device_node_id: incidentForm.device_node_id ? Number(incidentForm.device_node_id) : null,
    };
    try {
      await apiRequest<SafetyIncident>('/api/v1/safety/incidents', { method: 'POST', body: JSON.stringify(payload) });
      setIncidentForm(emptyIncidentForm());
      setShowIncidentForm(false);
      setNotice('Incident angelegt.');
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCalSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    const payload = {
      target_type: calForm.target_type,
      target_id: Number(calForm.target_id),
      parameter: calForm.parameter,
      status: calForm.status,
      calibrated_at: calForm.calibrated_at || null,
      due_at: calForm.due_at || null,
      calibration_value: calForm.calibration_value ? Number(calForm.calibration_value) : null,
      reference_value: calForm.reference_value ? Number(calForm.reference_value) : null,
      note: calForm.note || null,
    };
    try {
      await apiRequest<CalibrationRecord>('/api/v1/calibration', { method: 'POST', body: JSON.stringify(payload) });
      setCalForm(emptyCalibrationForm());
      setShowCalForm(false);
      setNotice('Kalibrierung angelegt.');
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMaintSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    const payload = {
      target_type: maintForm.target_type,
      target_id: Number(maintForm.target_id),
      maintenance_type: maintForm.maintenance_type,
      status: maintForm.status,
      performed_at: maintForm.performed_at || null,
      due_at: maintForm.due_at || null,
      note: maintForm.note || null,
    };
    try {
      await apiRequest<MaintenanceRecord>('/api/v1/maintenance', { method: 'POST', body: JSON.stringify(payload) });
      setMaintForm(emptyMaintenanceForm());
      setShowMaintForm(false);
      setNotice('Wartungseintrag angelegt.');
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function updateIncidentStatus(id: number, newStatus: IncidentStatus) {
    setActionLoadingId(id);
    setPageError(null);
    try {
      await apiRequest<SafetyIncident>(`/api/v1/safety/incidents/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      setNotice(`Incident #${id} aktualisiert.`);
      await loadData();
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setActionLoadingId(null);
    }
  }

  async function updateCalStatus(id: number, newStatus: CalibrationStatus) {
    setActionLoadingId(id);
    setPageError(null);
    try {
      await apiRequest<CalibrationRecord>(`/api/v1/calibration/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      setNotice(`Kalibrierung #${id} aktualisiert.`);
      await loadData();
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setActionLoadingId(null);
    }
  }

  async function updateMaintStatus(id: number, newStatus: MaintenanceStatus) {
    setActionLoadingId(id);
    setPageError(null);
    try {
      await apiRequest<MaintenanceRecord>(`/api/v1/maintenance/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      setNotice(`Wartung #${id} aktualisiert.`);
      await loadData();
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setActionLoadingId(null);
    }
  }

  const filteredIncidents = incStatusFilter
    ? incidents.filter((i) => i.status === incStatusFilter)
    : incidents;
  const filteredCalibrations = calStatusFilter
    ? calibrations.filter((c) => c.status === calStatusFilter)
    : calibrations;
  const filteredMaintenances = maintStatusFilter
    ? maintenances.filter((m) => m.status === maintStatusFilter)
    : maintenances;

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>Safety &amp; Betrieb</h1>

      {pageError && <InlineMessage tone="error">{pageError}</InlineMessage>}
      {notice && <InlineMessage tone="success">{notice}</InlineMessage>}

      {overview && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Offene Incidents</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: overview.open_incidents > 0 ? '#e53e3e' : '#2d3748' }}>{overview.open_incidents}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Kritisch</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: overview.critical_incidents > 0 ? '#c53030' : '#2d3748' }}>{overview.critical_incidents}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Kalibrierung F&auml;llig/Abgelaufen</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: overview.calibration_expired > 0 ? '#dd6b20' : '#2d3748' }}>{overview.calibration_expired}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Wartung &Uuml;berf&auml;llig</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: overview.maintenance_overdue > 0 ? '#dd6b20' : '#2d3748' }}>{overview.maintenance_overdue}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Blockierte Commands</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: overview.blocked_commands > 0 ? '#e53e3e' : '#2d3748' }}>{overview.blocked_commands}</div>
          </Card>
          <Card>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: 4 }}>Quittiert</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>{overview.acknowledged_incidents}</div>
          </Card>
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0' }}>
        {(['incidents', 'calibration', 'maintenance'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: tab === t ? '2px solid #3182ce' : '2px solid transparent',
              fontWeight: tab === t ? 700 : 400,
              cursor: 'pointer',
              color: tab === t ? '#3182ce' : '#4a5568',
            }}
          >
            {t === 'incidents' ? 'Incidents' : t === 'calibration' ? 'Kalibrierung' : 'Wartung'}
          </button>
        ))}
      </div>

      {loading && <div style={{ color: '#718096' }}>Laden…</div>}

      {tab === 'incidents' && !loading && (
        <div>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
            <select
              value={incStatusFilter}
              onChange={(e) => setIncStatusFilter(e.target.value)}
              style={{ padding: '0.35rem 0.5rem', borderRadius: 4, border: '1px solid #cbd5e0' }}
            >
              <option value="">Alle Status</option>
              {incidentStatusOptions.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <button
              onClick={() => { setShowIncidentForm((v) => !v); setFormError(null); }}
              style={{ marginLeft: 'auto', padding: '0.4rem 0.9rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
            >
              + Incident
            </button>
          </div>

          {showIncidentForm && (
            <Card style={{ marginBottom: '1rem' }}>
              <form onSubmit={(e) => { void handleIncidentSubmit(e); }}>
                <h3 style={{ marginBottom: '0.75rem' }}>Neues Incident</h3>
                {formError && <InlineMessage tone="error">{formError}</InlineMessage>}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <FormField label="Typ">
                    <select value={incidentForm.incident_type} onChange={(e) => setIncidentForm((f) => ({ ...f, incident_type: e.target.value as IncidentType }))} required>
                      {incidentTypeOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Schwere">
                    <select value={incidentForm.severity} onChange={(e) => setIncidentForm((f) => ({ ...f, severity: e.target.value as IncidentSeverity }))}>
                      {incidentSeverityOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Reaktor-ID (optional)">
                    <input type="number" value={incidentForm.reactor_id} onChange={(e) => setIncidentForm((f) => ({ ...f, reactor_id: e.target.value }))} />
                  </FormField>
                  <FormField label="Node-ID (optional)">
                    <input type="number" value={incidentForm.device_node_id} onChange={(e) => setIncidentForm((f) => ({ ...f, device_node_id: e.target.value }))} />
                  </FormField>
                  <FormField label="Titel" style={{ gridColumn: '1 / -1' }}>
                    <input type="text" value={incidentForm.title} onChange={(e) => setIncidentForm((f) => ({ ...f, title: e.target.value }))} required />
                  </FormField>
                  <FormField label="Beschreibung" style={{ gridColumn: '1 / -1' }}>
                    <textarea rows={3} value={incidentForm.description} onChange={(e) => setIncidentForm((f) => ({ ...f, description: e.target.value }))} />
                  </FormField>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                  <button type="submit" disabled={submitting} style={{ padding: '0.4rem 1rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    {submitting ? 'Speichere…' : 'Anlegen'}
                  </button>
                  <button type="button" onClick={() => setShowIncidentForm(false)} style={{ padding: '0.4rem 1rem', background: '#e2e8f0', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    Abbrechen
                  </button>
                </div>
              </form>
            </Card>
          )}

          {filteredIncidents.length === 0 && <div style={{ color: '#718096' }}>Keine Incidents.</div>}
          {filteredIncidents.map((inc) => (
            <Card key={inc.id} style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span className={severityBadge(inc.severity)} style={{ marginRight: 6 }}>{inc.severity.toUpperCase()}</span>
                  <span className={statusBadge(inc.status)} style={{ marginRight: 6 }}>{inc.status}</span>
                  <strong style={{ fontSize: '0.95rem' }}>{inc.title}</strong>
                  <div style={{ color: '#718096', fontSize: '0.8rem', marginTop: 2 }}>
                    #{inc.id} · {inc.incident_type} · {formatDateTime(inc.created_at)}
                    {inc.reactor_name && ` · Reaktor: ${inc.reactor_name}`}
                    {inc.device_node_name && ` · Node: ${inc.device_node_name}`}
                  </div>
                  {inc.description && <div style={{ marginTop: 4, fontSize: '0.85rem', color: '#4a5568' }}>{inc.description}</div>}
                  {inc.resolved_at && <div style={{ marginTop: 2, fontSize: '0.8rem', color: '#48bb78' }}>Geloest: {formatDateTime(inc.resolved_at)}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                  {inc.status === 'open' && (
                    <button
                      onClick={() => void updateIncidentStatus(inc.id, 'acknowledged')}
                      disabled={actionLoadingId === inc.id}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', background: '#ecc94b', border: 'none', borderRadius: 3, cursor: 'pointer' }}
                    >
                      Quittieren
                    </button>
                  )}
                  {inc.status !== 'resolved' && (
                    <button
                      onClick={() => void updateIncidentStatus(inc.id, 'resolved')}
                      disabled={actionLoadingId === inc.id}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', background: '#48bb78', color: '#fff', border: 'none', borderRadius: 3, cursor: 'pointer' }}
                    >
                      L&ouml;sen
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {tab === 'calibration' && !loading && (
        <div>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
            <select
              value={calStatusFilter}
              onChange={(e) => setCalStatusFilter(e.target.value)}
              style={{ padding: '0.35rem 0.5rem', borderRadius: 4, border: '1px solid #cbd5e0' }}
            >
              <option value="">Alle Status</option>
              {calibrationStatusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button
              onClick={() => { setShowCalForm((v) => !v); setFormError(null); }}
              style={{ marginLeft: 'auto', padding: '0.4rem 0.9rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
            >
              + Kalibrierung
            </button>
          </div>

          {showCalForm && (
            <Card style={{ marginBottom: '1rem' }}>
              <form onSubmit={(e) => { void handleCalSubmit(e); }}>
                <h3 style={{ marginBottom: '0.75rem' }}>Neue Kalibrierung</h3>
                {formError && <InlineMessage tone="error">{formError}</InlineMessage>}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <FormField label="Zieltyp">
                    <select value={calForm.target_type} onChange={(e) => setCalForm((f) => ({ ...f, target_type: e.target.value as CalibrationTargetType }))}>
                      {calibrationTargetTypeOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Ziel-ID">
                    <input type="number" value={calForm.target_id} onChange={(e) => setCalForm((f) => ({ ...f, target_id: e.target.value }))} required />
                  </FormField>
                  <FormField label="Parameter (z.B. ph, temp)">
                    <input type="text" value={calForm.parameter} onChange={(e) => setCalForm((f) => ({ ...f, parameter: e.target.value }))} required />
                  </FormField>
                  <FormField label="Status">
                    <select value={calForm.status} onChange={(e) => setCalForm((f) => ({ ...f, status: e.target.value as CalibrationStatus }))}>
                      {calibrationStatusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Kalibriert am">
                    <input type="datetime-local" value={calForm.calibrated_at} onChange={(e) => setCalForm((f) => ({ ...f, calibrated_at: e.target.value }))} />
                  </FormField>
                  <FormField label="F&auml;llig am">
                    <input type="datetime-local" value={calForm.due_at} onChange={(e) => setCalForm((f) => ({ ...f, due_at: e.target.value }))} />
                  </FormField>
                  <FormField label="Kalibrierwert">
                    <input type="number" step="any" value={calForm.calibration_value} onChange={(e) => setCalForm((f) => ({ ...f, calibration_value: e.target.value }))} />
                  </FormField>
                  <FormField label="Referenzwert">
                    <input type="number" step="any" value={calForm.reference_value} onChange={(e) => setCalForm((f) => ({ ...f, reference_value: e.target.value }))} />
                  </FormField>
                  <FormField label="Notiz" style={{ gridColumn: '1 / -1' }}>
                    <textarea rows={2} value={calForm.note} onChange={(e) => setCalForm((f) => ({ ...f, note: e.target.value }))} />
                  </FormField>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                  <button type="submit" disabled={submitting} style={{ padding: '0.4rem 1rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    {submitting ? 'Speichere…' : 'Anlegen'}
                  </button>
                  <button type="button" onClick={() => setShowCalForm(false)} style={{ padding: '0.4rem 1rem', background: '#e2e8f0', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    Abbrechen
                  </button>
                </div>
              </form>
            </Card>
          )}

          {filteredCalibrations.length === 0 && <div style={{ color: '#718096' }}>Keine Kalibrierungen.</div>}
          {filteredCalibrations.map((cal) => (
            <Card key={cal.id} style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span className={statusBadge(cal.status)} style={{ marginRight: 6 }}>{cal.status}</span>
                  <strong>{cal.parameter.toUpperCase()}</strong>
                  {cal.target_name && <span style={{ marginLeft: 6, color: '#4a5568' }}>{cal.target_type}: {cal.target_name}</span>}
                  <div style={{ color: '#718096', fontSize: '0.8rem', marginTop: 2 }}>
                    #{cal.id} · Kalibriert: {formatDateTime(cal.calibrated_at)} · F&auml;llig: {formatDateTime(cal.due_at)}
                    {cal.performed_by_username && ` · Durchgef&uuml;hrt von: ${cal.performed_by_username}`}
                  </div>
                  {(cal.calibration_value !== null || cal.reference_value !== null) && (
                    <div style={{ fontSize: '0.8rem', color: '#4a5568', marginTop: 2 }}>
                      Wert: {cal.calibration_value ?? '—'} · Referenz: {cal.reference_value ?? '—'}
                    </div>
                  )}
                  {cal.note && <div style={{ marginTop: 2, fontSize: '0.8rem', color: '#718096' }}>{cal.note}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                  {cal.status !== 'valid' && (
                    <button
                      onClick={() => void updateCalStatus(cal.id, 'valid')}
                      disabled={actionLoadingId === cal.id}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', background: '#48bb78', color: '#fff', border: 'none', borderRadius: 3, cursor: 'pointer' }}
                    >
                      Als g&uuml;ltig markieren
                    </button>
                  )}
                  {cal.status === 'valid' && (
                    <button
                      onClick={() => void updateCalStatus(cal.id, 'expired')}
                      disabled={actionLoadingId === cal.id}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', background: '#e2e8f0', border: 'none', borderRadius: 3, cursor: 'pointer' }}
                    >
                      Ablaufen lassen
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {tab === 'maintenance' && !loading && (
        <div>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
            <select
              value={maintStatusFilter}
              onChange={(e) => setMaintStatusFilter(e.target.value)}
              style={{ padding: '0.35rem 0.5rem', borderRadius: 4, border: '1px solid #cbd5e0' }}
            >
              <option value="">Alle Status</option>
              {maintenanceStatusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button
              onClick={() => { setShowMaintForm((v) => !v); setFormError(null); }}
              style={{ marginLeft: 'auto', padding: '0.4rem 0.9rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
            >
              + Wartung
            </button>
          </div>

          {showMaintForm && (
            <Card style={{ marginBottom: '1rem' }}>
              <form onSubmit={(e) => { void handleMaintSubmit(e); }}>
                <h3 style={{ marginBottom: '0.75rem' }}>Neuer Wartungseintrag</h3>
                {formError && <InlineMessage tone="error">{formError}</InlineMessage>}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <FormField label="Zieltyp">
                    <select value={maintForm.target_type} onChange={(e) => setMaintForm((f) => ({ ...f, target_type: e.target.value as MaintenanceTargetType }))}>
                      {maintenanceTargetTypeOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Ziel-ID">
                    <input type="number" value={maintForm.target_id} onChange={(e) => setMaintForm((f) => ({ ...f, target_id: e.target.value }))} required />
                  </FormField>
                  <FormField label="Wartungstyp">
                    <select value={maintForm.maintenance_type} onChange={(e) => setMaintForm((f) => ({ ...f, maintenance_type: e.target.value as MaintenanceType }))}>
                      {maintenanceTypeOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Status">
                    <select value={maintForm.status} onChange={(e) => setMaintForm((f) => ({ ...f, status: e.target.value as MaintenanceStatus }))}>
                      {maintenanceStatusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Durchgef&uuml;hrt am">
                    <input type="datetime-local" value={maintForm.performed_at} onChange={(e) => setMaintForm((f) => ({ ...f, performed_at: e.target.value }))} />
                  </FormField>
                  <FormField label="F&auml;llig am">
                    <input type="datetime-local" value={maintForm.due_at} onChange={(e) => setMaintForm((f) => ({ ...f, due_at: e.target.value }))} />
                  </FormField>
                  <FormField label="Notiz" style={{ gridColumn: '1 / -1' }}>
                    <textarea rows={2} value={maintForm.note} onChange={(e) => setMaintForm((f) => ({ ...f, note: e.target.value }))} />
                  </FormField>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                  <button type="submit" disabled={submitting} style={{ padding: '0.4rem 1rem', background: '#3182ce', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    {submitting ? 'Speichere…' : 'Anlegen'}
                  </button>
                  <button type="button" onClick={() => setShowMaintForm(false)} style={{ padding: '0.4rem 1rem', background: '#e2e8f0', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
                    Abbrechen
                  </button>
                </div>
              </form>
            </Card>
          )}

          {filteredMaintenances.length === 0 && <div style={{ color: '#718096' }}>Keine Wartungseintr&auml;ge.</div>}
          {filteredMaintenances.map((m) => (
            <Card key={m.id} style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span className={statusBadge(m.status)} style={{ marginRight: 6 }}>{m.status}</span>
                  <strong>{m.maintenance_type.replace(/_/g, ' ')}</strong>
                  {m.target_name && <span style={{ marginLeft: 6, color: '#4a5568' }}>{m.target_type}: {m.target_name}</span>}
                  <div style={{ color: '#718096', fontSize: '0.8rem', marginTop: 2 }}>
                    #{m.id} · F&auml;llig: {formatDateTime(m.due_at)} · Durchgef&uuml;hrt: {formatDateTime(m.performed_at)}
                    {m.performed_by_username && ` · von: ${m.performed_by_username}`}
                  </div>
                  {m.note && <div style={{ marginTop: 2, fontSize: '0.8rem', color: '#718096' }}>{m.note}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                  {m.status !== 'done' && (
                    <button
                      onClick={() => void updateMaintStatus(m.id, 'done')}
                      disabled={actionLoadingId === m.id}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', background: '#48bb78', color: '#fff', border: 'none', borderRadius: 3, cursor: 'pointer' }}
                    >
                      Als erledigt markieren
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
