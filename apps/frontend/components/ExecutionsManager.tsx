'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  ABrainExecutionLogEntry,
  ABrainExecutionStatusValue,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const STATUS_FILTERS: Array<{ value: ABrainExecutionStatusValue | ''; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'executed', label: 'Ausgeführt' },
  { value: 'pending_approval', label: 'Approval offen' },
  { value: 'blocked', label: 'Blockiert' },
  { value: 'rejected', label: 'Abgelehnt' },
  { value: 'failed', label: 'Fehlgeschlagen' },
];

const APPROVAL_FILTERS: Array<{ value: '' | 'with' | 'without'; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'with', label: 'Mit Approval' },
  { value: 'without', label: 'Ohne Approval' },
];

const statusTone: Record<string, 'info' | 'warning' | 'success' | 'error'> = {
  executed: 'success',
  pending_approval: 'warning',
  blocked: 'error',
  failed: 'error',
  rejected: 'info',
};

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unerwarteter Fehler';
}

function formatTimestamp(value: string | null): string {
  if (!value) return '-';
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function summarizeParams(params: Record<string, unknown>): string {
  const keys = Object.keys(params ?? {});
  if (keys.length === 0) return '—';
  return keys.slice(0, 4).map((key) => {
    const raw = params[key];
    let str: string;
    if (raw === null || raw === undefined) {
      str = String(raw);
    } else if (typeof raw === 'object') {
      str = JSON.stringify(raw);
    } else {
      str = String(raw);
    }
    if (str.length > 30) str = `${str.slice(0, 30)}…`;
    return `${key}=${str}`;
  }).join(', ');
}

function resultShort(result: Record<string, unknown>): string {
  if (!result || Object.keys(result).length === 0) return '—';
  const candidates = ['status', 'state', 'id', 'blocked_reason'];
  for (const key of candidates) {
    if (key in result) {
      const val = result[key];
      if (val !== null && val !== undefined) {
        return `${key}=${typeof val === 'object' ? JSON.stringify(val) : String(val)}`;
      }
    }
  }
  return `${Object.keys(result).length} Felder`;
}

export function ExecutionsManager() {
  const [executions, setExecutions] = useState<ABrainExecutionLogEntry[]>([]);
  const [statusFilter, setStatusFilter] = useState<ABrainExecutionStatusValue | ''>('');
  const [actionFilter, setActionFilter] = useState('');
  const [traceFilter, setTraceFilter] = useState('');
  const [executedByFilter, setExecutedByFilter] = useState('');
  const [approvalFilter, setApprovalFilter] = useState<'' | 'with' | 'without'>('');
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ABrainExecutionLogEntry | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  async function loadList() {
    setLoading(true);
    setLoadError(null);
    try {
      const query = new URLSearchParams();
      if (statusFilter) query.set('status', statusFilter);
      if (actionFilter.trim()) query.set('action', actionFilter.trim());
      if (traceFilter.trim()) query.set('trace_id', traceFilter.trim());
      if (executedByFilter.trim()) query.set('executed_by', executedByFilter.trim());
      if (approvalFilter === 'with') query.set('has_approval', 'true');
      if (approvalFilter === 'without') query.set('has_approval', 'false');
      const suffix = query.toString() ? `?${query.toString()}` : '';
      const data = await apiRequest<ABrainExecutionLogEntry[]>(
        `/api/v1/abrain/executions${suffix}`,
      );
      setExecutions(data);
    } catch (error) {
      setLoadError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(logId: number) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const data = await apiRequest<ABrainExecutionLogEntry>(
        `/api/v1/abrain/executions/${logId}`,
      );
      setDetail(data);
    } catch (error) {
      setDetailError(errorMessage(error));
      setDetail(null);
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    void loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, approvalFilter]);

  useEffect(() => {
    if (selectedId !== null) {
      void loadDetail(selectedId);
    } else {
      setDetail(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  function submitFilters(event: FormEvent) {
    event.preventDefault();
    void loadList();
  }

  const summary = useMemo(() => {
    const totals: Record<string, number> = {
      executed: 0,
      pending_approval: 0,
      blocked: 0,
      failed: 0,
      rejected: 0,
    };
    for (const log of executions) {
      totals[log.status] = (totals[log.status] ?? 0) + 1;
    }
    return totals;
  }, [executions]);

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h2>ABrain Executions</h2>
        <p className="muted">
          Audit-/Operator-Sicht auf jede ABrain-Aktion: ausgeführt, blockiert, abgelehnt oder
          pending. Jede Execution ist über <code>trace_id</code> mit Trace und optional mit
          einem Approval verknüpft.
        </p>
      </div>

      {loadError ? <InlineMessage tone="error">{loadError}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Übersicht">
          <div className="detailList">
            <div className="detailRow"><strong>Ausgeführt</strong><span>{summary.executed}</span></div>
            <div className="detailRow"><strong>Approval offen</strong><span>{summary.pending_approval}</span></div>
            <div className="detailRow"><strong>Blockiert</strong><span>{summary.blocked}</span></div>
            <div className="detailRow"><strong>Fehlgeschlagen</strong><span>{summary.failed}</span></div>
            <div className="detailRow"><strong>Abgelehnt</strong><span>{summary.rejected}</span></div>
          </div>
        </Card>
        <Card title="Filter">
          <form className="entityForm" onSubmit={submitFilters}>
            <FormField label="Status">
              <select
                className="input"
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(event.target.value as ABrainExecutionStatusValue | '')
                }
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Action">
              <input
                className="input"
                value={actionFilter}
                onChange={(event) => setActionFilter(event.target.value)}
                placeholder="labos.create_task"
              />
            </FormField>
            <FormField label="Trace ID">
              <input
                className="input"
                value={traceFilter}
                onChange={(event) => setTraceFilter(event.target.value)}
                placeholder="uuid…"
              />
            </FormField>
            <FormField label="Executed by">
              <input
                className="input"
                value={executedByFilter}
                onChange={(event) => setExecutedByFilter(event.target.value)}
                placeholder="username"
              />
            </FormField>
            <FormField label="Approval">
              <select
                className="input"
                value={approvalFilter}
                onChange={(event) =>
                  setApprovalFilter(event.target.value as '' | 'with' | 'without')
                }
              >
                {APPROVAL_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </FormField>
            <div className="buttonRow">
              <button className="button" type="submit">Filter anwenden</button>
            </div>
          </form>
        </Card>
        <Card title="Hinweis">
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            Read-only Audit-View. Keine Entscheidungslogik, keine Re-Execute. Für Freigaben
            siehe Approvals, für End-to-End-Timelines siehe Traces.
          </p>
        </Card>
      </div>

      <Card title="Executions">
        {loading ? (
          <InlineMessage>Lade Executions…</InlineMessage>
        ) : executions.length === 0 ? (
          <InlineMessage>Keine Executions für diesen Filter.</InlineMessage>
        ) : (
          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Angelegt</th>
                  <th>Action</th>
                  <th>Status</th>
                  <th>Blocked / Fehler</th>
                  <th>By</th>
                  <th>Trace</th>
                  <th>Approval</th>
                  <th>Params</th>
                  <th>Result</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {executions.map((log) => (
                  <tr key={log.id}>
                    <td>{formatTimestamp(log.created_at)}</td>
                    <td><code>{log.action}</code></td>
                    <td>
                      <span className={`badge badge-${statusTone[log.status] ?? 'info'}`}>
                        {log.status}
                      </span>
                    </td>
                    <td title={log.blocked_reason ?? ''}>
                      {log.blocked_reason ? log.blocked_reason.slice(0, 60) : '—'}
                    </td>
                    <td>
                      <div className="stackCompact">
                        <span>{log.executed_by ?? '—'}</span>
                        <span className="muted" style={{ fontSize: '0.75rem' }}>
                          {log.source ?? '—'}
                        </span>
                      </div>
                    </td>
                    <td>
                      {log.trace_id ? (
                        <Link href={`/traces`} title={log.trace_id}>
                          <code>{log.trace_id.slice(0, 8)}…</code>
                        </Link>
                      ) : '—'}
                    </td>
                    <td>
                      {log.approval_request_id !== null ? (
                        <Link href={`/approvals`}>#{log.approval_request_id}</Link>
                      ) : '—'}
                    </td>
                    <td>{summarizeParams(log.params)}</td>
                    <td>{resultShort(log.result)}</td>
                    <td>
                      <button
                        className="button buttonSecondary buttonCompact"
                        type="button"
                        onClick={() => setSelectedId(log.id)}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {selectedId !== null ? (
        <Card title={`Execution · #${selectedId}`}>
          {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}
          {detailLoading ? (
            <InlineMessage>Lade Execution…</InlineMessage>
          ) : detail ? (
            <div className="grid" style={{ gap: 16 }}>
              <div className="detailList">
                <div className="detailRow"><strong>Angelegt</strong><span>{formatTimestamp(detail.created_at)}</span></div>
                <div className="detailRow"><strong>Action</strong><span><code>{detail.action}</code></span></div>
                <div className="detailRow">
                  <strong>Status</strong>
                  <span className={`badge badge-${statusTone[detail.status] ?? 'info'}`}>
                    {detail.status}
                  </span>
                </div>
                <div className="detailRow"><strong>Blocked Reason</strong><span>{detail.blocked_reason ?? '—'}</span></div>
                <div className="detailRow"><strong>Source</strong><span>{detail.source ?? '—'}</span></div>
                <div className="detailRow"><strong>Executed by</strong><span>{detail.executed_by ?? '—'}</span></div>
                <div className="detailRow">
                  <strong>Trace</strong>
                  <span>
                    {detail.trace_id ? (
                      <Link href={`/traces`}><code>{detail.trace_id}</code></Link>
                    ) : '—'}
                  </span>
                </div>
                <div className="detailRow">
                  <strong>Approval</strong>
                  <span>
                    {detail.approval_request_id !== null ? (
                      <Link href={`/approvals`}>#{detail.approval_request_id}</Link>
                    ) : '—'}
                  </span>
                </div>
              </div>

              <div>
                <h3>Params</h3>
                <pre style={{ background: '#0b0f17', padding: 12, borderRadius: 8, overflow: 'auto', fontSize: '0.75rem' }}>
                  {JSON.stringify(detail.params, null, 2)}
                </pre>
              </div>

              <div>
                <h3>Result</h3>
                <pre style={{ background: '#0b0f17', padding: 12, borderRadius: 8, overflow: 'auto', fontSize: '0.75rem' }}>
                  {JSON.stringify(detail.result, null, 2)}
                </pre>
              </div>

              <div className="buttonRow">
                <button
                  className="button buttonSecondary"
                  type="button"
                  onClick={() => setSelectedId(null)}
                >
                  Schließen
                </button>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
