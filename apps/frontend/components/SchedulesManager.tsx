'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Reactor,
  Rule,
  Schedule,
  ScheduleExecution,
  ScheduleRunResponse,
  ScheduleTargetType,
  ScheduleType,
  scheduleTargetTypeOptions,
  scheduleTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type ScheduleFormState = {
  name: string;
  description: string;
  schedule_type: ScheduleType;
  interval_seconds: string;
  cron_expr: string;
  target_type: ScheduleTargetType;
  target_id: string;
  reactor_id: string;
  command_type: string;
  dry_run: boolean;
  is_enabled: boolean;
};

function createEmptyForm(): ScheduleFormState {
  return {
    name: '',
    description: '',
    schedule_type: 'interval',
    interval_seconds: '300',
    cron_expr: '',
    target_type: 'rule',
    target_id: '',
    reactor_id: '',
    command_type: 'light_on',
    dry_run: false,
    is_enabled: true,
  };
}

function toFormState(schedule: Schedule): ScheduleFormState {
  return {
    name: schedule.name,
    description: schedule.description ?? '',
    schedule_type: schedule.schedule_type,
    interval_seconds: schedule.interval_seconds ? String(schedule.interval_seconds) : '',
    cron_expr: schedule.cron_expr ?? '',
    target_type: schedule.target_type,
    target_id: schedule.target_id ? String(schedule.target_id) : '',
    reactor_id: schedule.reactor_id ? String(schedule.reactor_id) : '',
    command_type: (schedule.target_params?.command_type as string | undefined) ?? 'light_on',
    dry_run: Boolean(schedule.target_params?.dry_run),
    is_enabled: schedule.is_enabled,
  };
}

function formatDateTime(value: string | null) {
  if (!value) {
    return '-';
  }
  return new Date(value).toLocaleString('de-DE');
}

function describeSchedule(schedule: Schedule) {
  if (schedule.schedule_type === 'interval') {
    return `alle ${schedule.interval_seconds ?? '-'}s`;
  }
  if (schedule.schedule_type === 'cron') {
    return `cron ${schedule.cron_expr ?? ''}`;
  }
  return 'manuell';
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Unerwarteter Fehler';
}

export function SchedulesManager() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [executions, setExecutions] = useState<ScheduleExecution[]>([]);
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState<ScheduleFormState>(createEmptyForm);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadSchedules() {
    try {
      setLoading(true);
      const [schedulesData, reactorsData, rulesData] = await Promise.all([
        apiRequest<Schedule[]>('/api/v1/schedules'),
        apiRequest<Reactor[]>('/api/v1/reactors'),
        apiRequest<Rule[]>('/api/v1/rules'),
      ]);
      setSchedules(schedulesData);
      setReactors(reactorsData);
      setRules(rulesData);
      setPageError(null);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadExecutions(scheduleId: number) {
    try {
      const data = await apiRequest<ScheduleExecution[]>(
        `/api/v1/schedules/${scheduleId}/executions?limit=50`,
      );
      setExecutions(data);
    } catch (error) {
      setPageError(getErrorMessage(error));
    }
  }

  useEffect(() => {
    void loadSchedules();
  }, []);

  useEffect(() => {
    if (selectedId !== null) {
      void loadExecutions(selectedId);
    } else {
      setExecutions([]);
    }
  }, [selectedId]);

  function resetForm() {
    setForm(createEmptyForm());
    setMode('create');
    setEditingId(null);
    setFormError(null);
  }

  function startEditing(schedule: Schedule) {
    setForm(toFormState(schedule));
    setMode('edit');
    setEditingId(schedule.id);
    setFormError(null);
  }

  function buildPayload(state: ScheduleFormState) {
    const target_params: Record<string, unknown> = {};
    if (state.target_type === 'command') {
      target_params.command_type = state.command_type;
    } else if (state.target_type === 'rule') {
      target_params.dry_run = state.dry_run;
    }
    return {
      name: state.name.trim(),
      description: state.description.trim() || null,
      schedule_type: state.schedule_type,
      interval_seconds:
        state.schedule_type === 'interval' ? Number(state.interval_seconds) : null,
      cron_expr: state.schedule_type === 'cron' ? state.cron_expr.trim() : null,
      target_type: state.target_type,
      target_id:
        state.target_type === 'rule' && state.target_id ? Number(state.target_id) : null,
      reactor_id:
        state.target_type === 'command' && state.reactor_id ? Number(state.reactor_id) : null,
      target_params,
      is_enabled: state.is_enabled,
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);
    try {
      const payload = buildPayload(form);
      if (mode === 'create') {
        const schedule = await apiRequest<Schedule>('/api/v1/schedules', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice(`Schedule "${schedule.name}" angelegt.`);
      } else if (editingId !== null) {
        const schedule = await apiRequest<Schedule>(`/api/v1/schedules/${editingId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
        });
        setNotice(`Schedule "${schedule.name}" aktualisiert.`);
      }
      resetForm();
      await loadSchedules();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleEnabled(schedule: Schedule) {
    try {
      await apiRequest<Schedule>(`/api/v1/schedules/${schedule.id}/enabled`, {
        method: 'PATCH',
        body: JSON.stringify({ is_enabled: !schedule.is_enabled }),
      });
      await loadSchedules();
    } catch (error) {
      setPageError(getErrorMessage(error));
    }
  }

  async function runNow(schedule: Schedule) {
    setRunningId(schedule.id);
    try {
      const response = await apiRequest<ScheduleRunResponse>(
        `/api/v1/schedules/${schedule.id}/run`,
        { method: 'POST' },
      );
      setNotice(
        `Schedule "${response.schedule.name}" manuell ausgefuehrt (${response.execution.status}).`,
      );
      await loadSchedules();
      if (selectedId === schedule.id) {
        await loadExecutions(schedule.id);
      }
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setRunningId(null);
    }
  }

  async function deleteSchedule(schedule: Schedule) {
    if (!confirm(`Schedule "${schedule.name}" wirklich loeschen?`)) {
      return;
    }
    try {
      await apiRequest<void>(`/api/v1/schedules/${schedule.id}`, { method: 'DELETE' });
      setNotice(`Schedule "${schedule.name}" geloescht.`);
      if (selectedId === schedule.id) {
        setSelectedId(null);
      }
      if (editingId === schedule.id) {
        resetForm();
      }
      await loadSchedules();
    } catch (error) {
      setPageError(getErrorMessage(error));
    }
  }

  return (
    <div className="stackBlock">
      <Card title="Scheduler / Automation Runtime">
        <p className="muted">
          Zeitbasierte Automation fuer Reactor-Commands und Rules. Interval, Cron (Minute/Stunde/Tag/Monat/Wochentag)
          oder manuell.
        </p>
        {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
        {notice ? <InlineMessage tone="info">{notice}</InlineMessage> : null}
      </Card>

      <Card title={mode === 'create' ? 'Neuer Schedule' : `Schedule ${editingId} bearbeiten`}>
        <form onSubmit={handleSubmit} className="stackBlock">
          <div className="grid2">
            <FormField label="Name">
              <input
                className="input"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </FormField>
            <FormField label="Aktiv">
              <label className="checkboxRow">
                <input
                  type="checkbox"
                  checked={form.is_enabled}
                  onChange={(e) => setForm({ ...form, is_enabled: e.target.checked })}
                />
                <span>enabled</span>
              </label>
            </FormField>
          </div>
          <FormField label="Beschreibung">
            <textarea
              className="textarea"
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </FormField>
          <div className="grid2">
            <FormField label="Schedule-Typ">
              <select
                className="select"
                value={form.schedule_type}
                onChange={(e) =>
                  setForm({ ...form, schedule_type: e.target.value as ScheduleType })
                }
              >
                {scheduleTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            {form.schedule_type === 'interval' ? (
              <FormField label="Intervall (Sekunden)">
                <input
                  className="input"
                  type="number"
                  min={5}
                  value={form.interval_seconds}
                  onChange={(e) => setForm({ ...form, interval_seconds: e.target.value })}
                  required
                />
              </FormField>
            ) : form.schedule_type === 'cron' ? (
              <FormField label="Cron-Ausdruck (m h dom mon dow)">
                <input
                  className="input"
                  value={form.cron_expr}
                  onChange={(e) => setForm({ ...form, cron_expr: e.target.value })}
                  placeholder="0 7 * * *"
                  required
                />
              </FormField>
            ) : (
              <FormField label="Hinweis">
                <div className="muted">Manuelle Schedules laufen nur per &quot;Jetzt ausfuehren&quot;.</div>
              </FormField>
            )}
          </div>
          <div className="grid2">
            <FormField label="Ziel-Typ">
              <select
                className="select"
                value={form.target_type}
                onChange={(e) =>
                  setForm({ ...form, target_type: e.target.value as ScheduleTargetType })
                }
              >
                {scheduleTargetTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            {form.target_type === 'command' ? (
              <FormField label="Reaktor">
                <select
                  className="select"
                  value={form.reactor_id}
                  onChange={(e) => setForm({ ...form, reactor_id: e.target.value })}
                  required
                >
                  <option value="">Bitte waehlen...</option>
                  {reactors.map((reactor) => (
                    <option key={reactor.id} value={reactor.id}>
                      {reactor.name}
                    </option>
                  ))}
                </select>
              </FormField>
            ) : (
              <FormField label="Rule">
                <select
                  className="select"
                  value={form.target_id}
                  onChange={(e) => setForm({ ...form, target_id: e.target.value })}
                  required
                >
                  <option value="">Bitte waehlen...</option>
                  {rules.map((rule) => (
                    <option key={rule.id} value={rule.id}>
                      {rule.name}
                    </option>
                  ))}
                </select>
              </FormField>
            )}
          </div>
          {form.target_type === 'command' ? (
            <FormField label="Command-Typ">
              <select
                className="select"
                value={form.command_type}
                onChange={(e) => setForm({ ...form, command_type: e.target.value })}
              >
                {['light_on', 'light_off', 'pump_on', 'pump_off', 'aeration_start', 'aeration_stop', 'sample_capture'].map(
                  (option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ),
                )}
              </select>
            </FormField>
          ) : (
            <FormField label="Dry-Run">
              <label className="checkboxRow">
                <input
                  type="checkbox"
                  checked={form.dry_run}
                  onChange={(e) => setForm({ ...form, dry_run: e.target.checked })}
                />
                <span>Rule nur evaluieren, keine Aktion ausfuehren</span>
              </label>
            </FormField>
          )}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}
          <div className="buttonRow">
            <button className="button" type="submit" disabled={submitting}>
              {mode === 'create' ? 'Anlegen' : 'Aktualisieren'}
            </button>
            {mode === 'edit' ? (
              <button
                type="button"
                className="button buttonSecondary"
                onClick={resetForm}
                disabled={submitting}
              >
                Abbrechen
              </button>
            ) : null}
          </div>
        </form>
      </Card>

      <Card title="Schedules">
        {loading ? (
          <div className="muted">Lade Schedules...</div>
        ) : schedules.length === 0 ? (
          <div className="muted">Keine Schedules angelegt.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Ziel</th>
                <th>Aktiv</th>
                <th>Naechster Lauf</th>
                <th>Letzter Lauf</th>
                <th>Status</th>
                <th>Aktion</th>
              </tr>
            </thead>
            <tbody>
              {schedules.map((schedule) => (
                <tr
                  key={schedule.id}
                  className={selectedId === schedule.id ? 'tableRowActive' : undefined}
                  onClick={() => setSelectedId(schedule.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>
                    <strong>{schedule.name}</strong>
                    {schedule.description ? (
                      <div className="muted">{schedule.description}</div>
                    ) : null}
                  </td>
                  <td>{describeSchedule(schedule)}</td>
                  <td>
                    {schedule.target_type === 'command'
                      ? `cmd ${(schedule.target_params?.command_type as string | undefined) ?? ''} @ reactor ${schedule.reactor_id ?? '-'}`
                      : `rule ${schedule.target_id ?? '-'}`}
                  </td>
                  <td>{schedule.is_enabled ? 'an' : 'aus'}</td>
                  <td>{formatDateTime(schedule.next_run_at)}</td>
                  <td>{formatDateTime(schedule.last_run_at)}</td>
                  <td>
                    {schedule.last_status ? (
                      <span className={`badge badge-${schedule.last_status === 'success' ? 'success' : 'error'}`}>
                        {schedule.last_status}
                      </span>
                    ) : (
                      <span className="muted">-</span>
                    )}
                    {schedule.last_error ? (
                      <div className="muted">{schedule.last_error}</div>
                    ) : null}
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <div className="buttonRow">
                      <button
                        type="button"
                        className="button buttonSmall"
                        onClick={() => runNow(schedule)}
                        disabled={runningId === schedule.id}
                      >
                        {runningId === schedule.id ? 'laeuft...' : 'Jetzt'}
                      </button>
                      <button
                        type="button"
                        className="button buttonSecondary buttonSmall"
                        onClick={() => toggleEnabled(schedule)}
                      >
                        {schedule.is_enabled ? 'Pause' : 'Start'}
                      </button>
                      <button
                        type="button"
                        className="button buttonSecondary buttonSmall"
                        onClick={() => startEditing(schedule)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="button buttonDanger buttonSmall"
                        onClick={() => deleteSchedule(schedule)}
                      >
                        Del
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {selectedId !== null ? (
        <Card title={`Ausfuehrungen fuer Schedule ${selectedId}`}>
          {executions.length === 0 ? (
            <div className="muted">Noch keine Ausfuehrungen.</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Start</th>
                  <th>Trigger</th>
                  <th>Status</th>
                  <th>Ergebnis</th>
                </tr>
              </thead>
              <tbody>
                {executions.map((execution) => (
                  <tr key={execution.id}>
                    <td>{formatDateTime(execution.started_at)}</td>
                    <td>{execution.trigger}</td>
                    <td>
                      <span className={`badge badge-${execution.status === 'success' ? 'success' : 'error'}`}>
                        {execution.status}
                      </span>
                    </td>
                    <td>
                      {execution.error ? (
                        <span className="muted">{execution.error}</span>
                      ) : (
                        <code>{JSON.stringify(execution.result)}</code>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      ) : null}
    </div>
  );
}
