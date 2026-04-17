'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Alert,
  AlertSeverity,
  AlertSourceType,
  AlertStatus,
  alertSeverityOptions,
  alertSourceTypeOptions,
  alertStatusOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type AlertFormState = {
  title: string;
  message: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source_type: AlertSourceType;
  source_id: string;
};

type AlertFilters = {
  status: string;
  severity: string;
};

function createEmptyAlertForm(): AlertFormState {
  return {
    title: '',
    message: '',
    severity: 'warning',
    status: 'open',
    source_type: 'manual',
    source_id: '',
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
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

function badgeClass(tone: string) {
  return `badge badge-${tone}`;
}

export function AlertManager() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filters, setFilters] = useState<AlertFilters>({ status: '', severity: '' });
  const [form, setForm] = useState<AlertFormState>(createEmptyAlertForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadData(nextFilters: AlertFilters = filters) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.severity) params.set('severity', nextFilters.severity);
    const path = params.size > 0 ? `/api/v1/alerts?${params.toString()}` : '/api/v1/alerts';

    try {
      const data = await apiRequest<Alert[]>(path);
      setAlerts(data);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData(filters);
  }, []);

  function setFormValue<Key extends keyof AlertFormState>(key: Key, value: AlertFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    const payload = {
      title: form.title,
      message: form.message,
      severity: form.severity,
      status: form.status,
      source_type: form.source_type,
      source_id: form.source_id ? Number(form.source_id) : null,
    };

    try {
      await apiRequest<Alert>('/api/v1/alerts', { method: 'POST', body: JSON.stringify(payload) });
      setForm(createEmptyAlertForm());
      setNotice('Alert angelegt.');
      await loadData(filters);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function runAction(alertId: number, action: 'ack' | 'resolve', label: string) {
    setActionLoadingId(alertId);
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<Alert>(`/api/v1/alerts/${alertId}/${action}`, { method: 'PATCH' });
      setNotice(label);
      await loadData(filters);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setActionLoadingId(null);
    }
  }

  async function applyFilters(nextFilters: AlertFilters) {
    setFilters(nextFilters);
    await loadData(nextFilters);
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Alerts</h1>
        <p className="muted">Warnungen sichtbar machen, quittieren und aufgeloeste Meldungen nachvollziehbar abarbeiten.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="Manuellen Alert anlegen">
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Titel">
                <input className="input" value={form.title} onChange={(event) => setFormValue('title', event.target.value)} required />
              </FormField>

              <FormField label="Severity">
                <select className="input" value={form.severity} onChange={(event) => setFormValue('severity', event.target.value as AlertSeverity)}>
                  {alertSeverityOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Status">
                <select className="input" value={form.status} onChange={(event) => setFormValue('status', event.target.value as AlertStatus)}>
                  {alertStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Quelle">
                <select className="input" value={form.source_type} onChange={(event) => setFormValue('source_type', event.target.value as AlertSourceType)}>
                  {alertSourceTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Source ID (optional)">
                <input className="input" type="number" min="1" value={form.source_id} onChange={(event) => setFormValue('source_id', event.target.value)} />
              </FormField>
            </div>

            <FormField label="Meldung">
              <textarea className="input textarea" rows={5} value={form.message} onChange={(event) => setFormValue('message', event.target.value)} required />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : 'Alert anlegen'}
              </button>
            </div>
          </form>
        </Card>

        <Card title="Alert-Liste">
          <div className="formGrid">
            <FormField label="Statusfilter">
              <select className="input" value={filters.status} onChange={(event) => void applyFilters({ ...filters, status: event.target.value })}>
                <option value="">Alle</option>
                {alertStatusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField label="Severityfilter">
              <select className="input" value={filters.severity} onChange={(event) => void applyFilters({ ...filters, severity: event.target.value })}>
                <option value="">Alle</option>
                {alertSeverityOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
          </div>

          {loading ? (
            <InlineMessage>Lade Alerts…</InlineMessage>
          ) : alerts.length === 0 ? (
            <InlineMessage>Keine Alerts fuer den aktuellen Filter vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Titel</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Quelle</th>
                    <th>Zeitpunkte</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.id}>
                      <td>
                        <div className="stackCompact">
                          <strong>{alert.title}</strong>
                          <span className="muted">{alert.message}</span>
                        </div>
                      </td>
                      <td><span className={badgeClass(alert.severity)}>{alert.severity}</span></td>
                      <td><span className={badgeClass(alert.status)}>{alert.status}</span></td>
                      <td>{alert.source_id ? `${alert.source_type} #${alert.source_id}` : alert.source_type}</td>
                      <td>
                        <div className="stackCompact">
                          <span className="muted">Erstellt: {formatDateTime(alert.created_at)}</span>
                          <span className="muted">Quittiert: {formatDateTime(alert.acknowledged_at)}</span>
                          <span className="muted">Geloest: {formatDateTime(alert.resolved_at)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="buttonRow">
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={actionLoadingId === alert.id || alert.status !== 'open'}
                            onClick={() => void runAction(alert.id, 'ack', `${alert.title} quittiert.`)}
                          >
                            Ack
                          </button>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={actionLoadingId === alert.id || alert.status === 'resolved'}
                            onClick={() => void runAction(alert.id, 'resolve', `${alert.title} aufgeloest.`)}
                          >
                            Resolve
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
