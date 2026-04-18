'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  alertSeverityOptions,
  ReactorBiologicalState,
  reactorBiologicalStateOptions,
  ReactorContaminationState,
  reactorContaminationStateOptions,
  ReactorEventType,
  reactorEventTypeOptions,
  ReactorPhase,
  reactorPhaseOptions,
  ReactorTechnicalState,
  reactorTechnicalStateOptions,
  ReactorTwin,
  ReactorTwinDetail,
} from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type TwinFormState = {
  culture_type: string;
  strain: string;
  medium_recipe: string;
  inoculated_at: string;
  current_phase: ReactorPhase;
  target_ph_min: string;
  target_ph_max: string;
  target_temp_min: string;
  target_temp_max: string;
  target_light_min: string;
  target_light_max: string;
  target_flow_min: string;
  target_flow_max: string;
  expected_harvest_window_start: string;
  expected_harvest_window_end: string;
  contamination_state: ReactorContaminationState | '';
  technical_state: ReactorTechnicalState;
  biological_state: ReactorBiologicalState;
  notes: string;
};

type EventFormState = {
  event_type: ReactorEventType;
  title: string;
  description: string;
  severity: '' | 'info' | 'warning' | 'high' | 'critical';
  phase_snapshot: ReactorPhase | '';
};

function createEmptyTwinForm(): TwinFormState {
  return {
    culture_type: '',
    strain: '',
    medium_recipe: '',
    inoculated_at: '',
    current_phase: 'growth',
    target_ph_min: '',
    target_ph_max: '',
    target_temp_min: '',
    target_temp_max: '',
    target_light_min: '',
    target_light_max: '',
    target_flow_min: '',
    target_flow_max: '',
    expected_harvest_window_start: '',
    expected_harvest_window_end: '',
    contamination_state: '',
    technical_state: 'nominal',
    biological_state: 'unknown',
    notes: '',
  };
}

function createEmptyEventForm(phase: ReactorPhase = 'growth'): EventFormState {
  return {
    event_type: 'observation',
    title: '',
    description: '',
    severity: '',
    phase_snapshot: phase,
  };
}

function toTwinFormState(detail: ReactorTwinDetail): TwinFormState {
  return {
    culture_type: detail.culture_type ?? '',
    strain: detail.strain ?? '',
    medium_recipe: detail.medium_recipe ?? '',
    inoculated_at: detail.inoculated_at ? detail.inoculated_at.slice(0, 16) : '',
    current_phase: detail.current_phase,
    target_ph_min: detail.target_ph_min === null ? '' : String(detail.target_ph_min),
    target_ph_max: detail.target_ph_max === null ? '' : String(detail.target_ph_max),
    target_temp_min: detail.target_temp_min === null ? '' : String(detail.target_temp_min),
    target_temp_max: detail.target_temp_max === null ? '' : String(detail.target_temp_max),
    target_light_min: detail.target_light_min === null ? '' : String(detail.target_light_min),
    target_light_max: detail.target_light_max === null ? '' : String(detail.target_light_max),
    target_flow_min: detail.target_flow_min === null ? '' : String(detail.target_flow_min),
    target_flow_max: detail.target_flow_max === null ? '' : String(detail.target_flow_max),
    expected_harvest_window_start: detail.expected_harvest_window_start ? detail.expected_harvest_window_start.slice(0, 16) : '',
    expected_harvest_window_end: detail.expected_harvest_window_end ? detail.expected_harvest_window_end.slice(0, 16) : '',
    contamination_state: detail.contamination_state ?? '',
    technical_state: detail.technical_state,
    biological_state: detail.biological_state,
    notes: detail.notes ?? '',
  };
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function formatDateTime(value: string | null) {
  if (!value) {
    return 'Nicht dokumentiert';
  }
  return new Date(value).toLocaleString('de-DE');
}

function formatRange(minValue: number | null, maxValue: number | null, unit: string) {
  if (minValue === null && maxValue === null) {
    return 'Nicht gesetzt';
  }
  const minLabel = minValue === null ? 'offen' : `${minValue}`;
  const maxLabel = maxValue === null ? 'offen' : `${maxValue}`;
  return `${minLabel} bis ${maxLabel} ${unit}`.trim();
}

function getOptionLabel<T extends string>(options: ReadonlyArray<{ value: T; label: string }>, value: T | '' | null) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return options.find((option) => option.value === value)?.label ?? value;
}

function toNumberOrNull(value: string) {
  if (!value.trim()) {
    return null;
  }
  return Number(value);
}

export function ReactorOpsManager() {
  const { user } = useAuth();
  const canEdit = user?.role === 'admin' || user?.role === 'operator';
  const [items, setItems] = useState<ReactorTwin[]>([]);
  const [selectedReactorId, setSelectedReactorId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ReactorTwinDetail | null>(null);
  const [twinForm, setTwinForm] = useState<TwinFormState>(createEmptyTwinForm);
  const [eventForm, setEventForm] = useState<EventFormState>(createEmptyEventForm);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [savingTwin, setSavingTwin] = useState(false);
  const [savingEvent, setSavingEvent] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [eventError, setEventError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadOverview(preferredReactorId?: number | null) {
    setLoading(true);
    setPageError(null);
    try {
      const nextItems = await apiRequest<ReactorTwin[]>('/api/v1/reactor-ops');
      setItems(nextItems);
      const nextSelectedId =
        preferredReactorId && nextItems.some((item) => item.reactor_id === preferredReactorId)
          ? preferredReactorId
          : selectedReactorId && nextItems.some((item) => item.reactor_id === selectedReactorId)
            ? selectedReactorId
            : nextItems[0]?.reactor_id ?? null;
      setSelectedReactorId(nextSelectedId);
      if (nextSelectedId !== null) {
        await loadDetail(nextSelectedId);
      } else {
        setDetail(null);
      }
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(reactorId: number) {
    setDetailLoading(true);
    setFormError(null);
    setEventError(null);
    try {
      const nextDetail = await apiRequest<ReactorTwinDetail>(`/api/v1/reactor-ops/${reactorId}`);
      setDetail(nextDetail);
      setTwinForm(toTwinFormState(nextDetail));
      setEventForm(createEmptyEventForm(nextDetail.current_phase));
      setSelectedReactorId(reactorId);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    void loadOverview();
  }, []);

  function setTwinFormValue<Key extends keyof TwinFormState>(key: Key, value: TwinFormState[Key]) {
    setTwinForm((current) => ({ ...current, [key]: value }));
  }

  function setEventFormValue<Key extends keyof EventFormState>(key: Key, value: EventFormState[Key]) {
    setEventForm((current) => ({ ...current, [key]: value }));
  }

  async function handleTwinSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedReactorId) {
      return;
    }

    setSavingTwin(true);
    setFormError(null);
    setNotice(null);

    try {
      await apiRequest<ReactorTwin>(`/api/v1/reactor-ops/${selectedReactorId}`, {
        method: 'PUT',
        body: JSON.stringify({
          culture_type: twinForm.culture_type || null,
          strain: twinForm.strain || null,
          medium_recipe: twinForm.medium_recipe || null,
          inoculated_at: twinForm.inoculated_at || null,
          current_phase: twinForm.current_phase,
          target_ph_min: toNumberOrNull(twinForm.target_ph_min),
          target_ph_max: toNumberOrNull(twinForm.target_ph_max),
          target_temp_min: toNumberOrNull(twinForm.target_temp_min),
          target_temp_max: toNumberOrNull(twinForm.target_temp_max),
          target_light_min: toNumberOrNull(twinForm.target_light_min),
          target_light_max: toNumberOrNull(twinForm.target_light_max),
          target_flow_min: toNumberOrNull(twinForm.target_flow_min),
          target_flow_max: toNumberOrNull(twinForm.target_flow_max),
          expected_harvest_window_start: twinForm.expected_harvest_window_start || null,
          expected_harvest_window_end: twinForm.expected_harvest_window_end || null,
          contamination_state: twinForm.contamination_state || null,
          technical_state: twinForm.technical_state,
          biological_state: twinForm.biological_state,
          notes: twinForm.notes || null,
        }),
      });
      setNotice('Reactor Twin gespeichert.');
      await loadOverview(selectedReactorId);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSavingTwin(false);
    }
  }

  async function handleEventSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedReactorId) {
      return;
    }

    setSavingEvent(true);
    setEventError(null);
    setNotice(null);

    try {
      await apiRequest(`/api/v1/reactors/${selectedReactorId}/events`, {
        method: 'POST',
        body: JSON.stringify({
          event_type: eventForm.event_type,
          title: eventForm.title,
          description: eventForm.description || null,
          severity: eventForm.severity || null,
          phase_snapshot: eventForm.phase_snapshot || null,
        }),
      });
      setNotice('Reactor Event angelegt.');
      if (detail) {
        setEventForm(createEmptyEventForm(detail.current_phase));
      }
      await loadOverview(selectedReactorId);
    } catch (error) {
      setEventError(getErrorMessage(error));
    } finally {
      setSavingEvent(false);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>ReactorOps / Digital Twin</h1>
        <p className="muted">
          Betriebsansicht fuer biologische und technische Prozesszustaende, Zielbereiche, Ereignisse und die naechste Ausbaustufe Richtung Telemetry, Calibration und Safety.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="Reaktor-Uebersicht">
          {loading ? (
            <InlineMessage>Lade ReactorOps-Daten…</InlineMessage>
          ) : items.length === 0 ? (
            <p className="muted">Noch keine Reaktoren vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Reaktor</th>
                    <th>Phase</th>
                    <th>Tech</th>
                    <th>Bio</th>
                    <th>Tasks</th>
                    <th>Alerts</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.reactor_id}>
                      <td>
                        <button className="linkButton" type="button" onClick={() => void loadDetail(item.reactor_id)}>
                          <div className="stackCompact">
                            <strong>{item.reactor_name}</strong>
                            <span className="muted">{item.current_charge?.name || item.culture_type || item.reactor_type}</span>
                          </div>
                        </button>
                      </td>
                      <td><span className={`badge badge-${item.current_phase}`}>{getOptionLabel(reactorPhaseOptions, item.current_phase)}</span></td>
                      <td><span className={`badge badge-${item.technical_state}`}>{getOptionLabel(reactorTechnicalStateOptions, item.technical_state)}</span></td>
                      <td><span className={`badge badge-${item.biological_state}`}>{getOptionLabel(reactorBiologicalStateOptions, item.biological_state)}</span></td>
                      <td>{item.open_task_count}</td>
                      <td>{item.open_alert_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title={detail ? `${detail.reactor_name} Twin` : 'Reactor Twin'}>
          {detailLoading ? <InlineMessage>Lade Detailansicht…</InlineMessage> : null}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}
          {!detail ? (
            <p className="muted">Waehle einen Reaktor aus der Uebersicht.</p>
          ) : (
            <div className="stackBlock">
              <div className="detailList">
                <div className="detailRow">
                  <span className="muted">Reaktorstatus</span>
                  <span className={`badge badge-${detail.reactor_status}`}>{detail.reactor_status}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Twin konfiguriert</span>
                  <span>{detail.is_configured ? 'Ja' : 'Noch nicht persistiert'}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Aktive Charge</span>
                  <span>{detail.current_charge?.name || 'Keine aktive Charge'}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Letztes Event</span>
                  <span>{detail.latest_event?.title || 'Noch kein Event'}</span>
                </div>
              </div>

              <form className="entityForm" onSubmit={handleTwinSubmit}>
                <div className="formGrid">
                  <FormField label="Culture Type">
                    <input className="input" value={twinForm.culture_type} onChange={(event) => setTwinFormValue('culture_type', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Strain">
                    <input className="input" value={twinForm.strain} onChange={(event) => setTwinFormValue('strain', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Medium Recipe">
                    <input className="input" value={twinForm.medium_recipe} onChange={(event) => setTwinFormValue('medium_recipe', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Inokuliert am">
                    <input className="input" type="datetime-local" value={twinForm.inoculated_at} onChange={(event) => setTwinFormValue('inoculated_at', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Aktuelle Phase">
                    <select className="input" value={twinForm.current_phase} onChange={(event) => setTwinFormValue('current_phase', event.target.value as ReactorPhase)} disabled={!canEdit}>
                      {reactorPhaseOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Technical State">
                    <select className="input" value={twinForm.technical_state} onChange={(event) => setTwinFormValue('technical_state', event.target.value as ReactorTechnicalState)} disabled={!canEdit}>
                      {reactorTechnicalStateOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Biological State">
                    <select className="input" value={twinForm.biological_state} onChange={(event) => setTwinFormValue('biological_state', event.target.value as ReactorBiologicalState)} disabled={!canEdit}>
                      {reactorBiologicalStateOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Contamination State">
                    <select className="input" value={twinForm.contamination_state} onChange={(event) => setTwinFormValue('contamination_state', event.target.value as ReactorContaminationState | '')} disabled={!canEdit}>
                      <option value="">Nicht gesetzt</option>
                      {reactorContaminationStateOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="pH min">
                    <input className="input" type="number" step="0.1" value={twinForm.target_ph_min} onChange={(event) => setTwinFormValue('target_ph_min', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="pH max">
                    <input className="input" type="number" step="0.1" value={twinForm.target_ph_max} onChange={(event) => setTwinFormValue('target_ph_max', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Temperatur min">
                    <input className="input" type="number" step="0.1" value={twinForm.target_temp_min} onChange={(event) => setTwinFormValue('target_temp_min', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Temperatur max">
                    <input className="input" type="number" step="0.1" value={twinForm.target_temp_max} onChange={(event) => setTwinFormValue('target_temp_max', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Licht min">
                    <input className="input" type="number" step="0.1" value={twinForm.target_light_min} onChange={(event) => setTwinFormValue('target_light_min', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Licht max">
                    <input className="input" type="number" step="0.1" value={twinForm.target_light_max} onChange={(event) => setTwinFormValue('target_light_max', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Flow min">
                    <input className="input" type="number" step="0.1" value={twinForm.target_flow_min} onChange={(event) => setTwinFormValue('target_flow_min', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Flow max">
                    <input className="input" type="number" step="0.1" value={twinForm.target_flow_max} onChange={(event) => setTwinFormValue('target_flow_max', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Harvest Window Start">
                    <input className="input" type="datetime-local" value={twinForm.expected_harvest_window_start} onChange={(event) => setTwinFormValue('expected_harvest_window_start', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Harvest Window End">
                    <input className="input" type="datetime-local" value={twinForm.expected_harvest_window_end} onChange={(event) => setTwinFormValue('expected_harvest_window_end', event.target.value)} disabled={!canEdit} />
                  </FormField>
                </div>

                <FormField label="Notizen">
                  <textarea className="input textarea" value={twinForm.notes} onChange={(event) => setTwinFormValue('notes', event.target.value)} disabled={!canEdit} />
                </FormField>

                {canEdit ? (
                  <div className="buttonRow">
                    <button className="button" type="submit" disabled={savingTwin}>
                      {savingTwin ? 'Speichert…' : 'Twin speichern'}
                    </button>
                  </div>
                ) : (
                  <p className="muted">Viewer sehen ReactorOps read-only. Operatoren und Admins duerfen Twin- und Event-Daten pflegen.</p>
                )}
              </form>
            </div>
          )}
        </Card>
      </div>

      {detail ? (
        <>
          <div className="grid cols-2">
            <Card title="Prozesskontext">
              <div className="detailList">
                <div className="detailRow">
                  <span className="muted">pH Zielbereich</span>
                  <span>{formatRange(detail.target_ph_min, detail.target_ph_max, '')}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Temperatur Zielbereich</span>
                  <span>{formatRange(detail.target_temp_min, detail.target_temp_max, '°C')}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Licht Zielbereich</span>
                  <span>{formatRange(detail.target_light_min, detail.target_light_max, 'µmol')}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Flow Zielbereich</span>
                  <span>{formatRange(detail.target_flow_min, detail.target_flow_max, 'l/min')}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Harvest Window</span>
                  <span>{`${formatDateTime(detail.expected_harvest_window_start)} bis ${formatDateTime(detail.expected_harvest_window_end)}`}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Sensoren</span>
                  <span>{detail.sensor_count}</span>
                </div>
                <div className="detailRow">
                  <span className="muted">Fotos</span>
                  <span>{detail.photo_count}</span>
                </div>
              </div>
              <div className="buttonRow">
                <a className="button buttonSecondary" href="/reactors">Reactor CRUD</a>
                <a className="button buttonSecondary" href="/sensors">Sensorik</a>
                <a className="button buttonSecondary" href="/tasks">Tasks</a>
                <a className="button buttonSecondary" href="/alerts">Alerts</a>
                <a className="button buttonSecondary" href="/photos">Fotos</a>
              </div>
            </Card>

            <Card title="Neues Reactor Event">
              {eventError ? <InlineMessage tone="error">{eventError}</InlineMessage> : null}
              <form className="entityForm" onSubmit={handleEventSubmit}>
                <div className="formGrid">
                  <FormField label="Event Type">
                    <select className="input" value={eventForm.event_type} onChange={(event) => setEventFormValue('event_type', event.target.value as ReactorEventType)} disabled={!canEdit}>
                      {reactorEventTypeOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Severity">
                    <select className="input" value={eventForm.severity} onChange={(event) => setEventFormValue('severity', event.target.value as EventFormState['severity'])} disabled={!canEdit}>
                      <option value="">Nicht gesetzt</option>
                      {alertSeverityOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Titel">
                    <input className="input" value={eventForm.title} onChange={(event) => setEventFormValue('title', event.target.value)} disabled={!canEdit} required />
                  </FormField>

                  <FormField label="Phase Snapshot">
                    <select className="input" value={eventForm.phase_snapshot} onChange={(event) => setEventFormValue('phase_snapshot', event.target.value as ReactorPhase | '')} disabled={!canEdit}>
                      <option value="">Automatisch aus Twin</option>
                      {reactorPhaseOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>
                </div>

                <FormField label="Beschreibung">
                  <textarea className="input textarea" value={eventForm.description} onChange={(event) => setEventFormValue('description', event.target.value)} disabled={!canEdit} />
                </FormField>

                {canEdit ? (
                  <div className="buttonRow">
                    <button className="button" type="submit" disabled={savingEvent}>
                      {savingEvent ? 'Speichert…' : 'Event anlegen'}
                    </button>
                  </div>
                ) : (
                  <p className="muted">Nur Operatoren und Admins duerfen neue Reactor Events dokumentieren.</p>
                )}
              </form>
            </Card>
          </div>

          <div className="grid cols-2">
            <Card title="Event-Historie">
              {detail.recent_events.length === 0 ? (
                <p className="muted">Noch keine Reactor Events vorhanden.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Zeit</th>
                        <th>Typ</th>
                        <th>Titel</th>
                        <th>Phase</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.recent_events.map((event) => (
                        <tr key={event.id}>
                          <td>{new Date(event.created_at).toLocaleString('de-DE')}</td>
                          <td><span className={`badge badge-${event.severity || 'info'}`}>{getOptionLabel(reactorEventTypeOptions, event.event_type)}</span></td>
                          <td>
                            <div className="stackCompact">
                              <strong>{event.title}</strong>
                              <span className="muted">{event.created_by_username || 'System / Seed'}</span>
                            </div>
                          </td>
                          <td>{getOptionLabel(reactorPhaseOptions, event.phase_snapshot)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Offene Tasks">
              {detail.open_tasks.length === 0 ? (
                <p className="muted">Keine offenen Tasks fuer diesen Reaktor.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Titel</th>
                        <th>Status</th>
                        <th>Prioritaet</th>
                        <th>Faellig</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.open_tasks.map((task) => (
                        <tr key={task.id}>
                          <td>{task.title}</td>
                          <td><span className={`badge badge-${task.status}`}>{task.status}</span></td>
                          <td><span className={`badge badge-${task.priority}`}>{task.priority}</span></td>
                          <td>{formatDateTime(task.due_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Letzte Alerts">
              {detail.recent_alerts.length === 0 ? (
                <p className="muted">Keine reaktorspezifischen Alerts vorhanden.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Titel</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Erstellt</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.recent_alerts.map((alert) => (
                        <tr key={alert.id}>
                          <td>{alert.title}</td>
                          <td><span className={`badge badge-${alert.severity}`}>{alert.severity}</span></td>
                          <td><span className={`badge badge-${alert.status}`}>{alert.status}</span></td>
                          <td>{new Date(alert.created_at).toLocaleString('de-DE')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Letzte Fotos">
              {detail.recent_photos.length === 0 ? (
                <p className="muted">Noch keine Fotos fuer diesen Reaktor vorhanden.</p>
              ) : (
                <div className="photoGrid">
                  {detail.recent_photos.map((photo) => (
                    <a key={photo.id} href={`${apiBase}${photo.file_url}`} target="_blank" rel="noreferrer" className="photoTile">
                      <img className="photoThumb" src={`${apiBase}${photo.file_url}`} alt={photo.title || photo.original_filename} />
                      <div className="photoMeta">
                        <strong>{photo.title || photo.original_filename}</strong>
                        <span className="muted">{formatDateTime(photo.created_at)}</span>
                      </div>
                    </a>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
