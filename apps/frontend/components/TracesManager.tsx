'use client';

import { useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  TraceContext,
  TraceContextDetail,
  TraceContextSource,
  TraceContextStatus,
  TraceTimelineEvent,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const STATUS_FILTERS: Array<{ value: TraceContextStatus | ''; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'open', label: 'Offen' },
  { value: 'completed', label: 'Abgeschlossen' },
  { value: 'failed', label: 'Fehlgeschlagen' },
];

const SOURCE_FILTERS: Array<{ value: TraceContextSource | ''; label: string }> = [
  { value: '', label: 'Alle Quellen' },
  { value: 'abrain', label: 'ABrain' },
  { value: 'local', label: 'Lokal' },
  { value: 'operator', label: 'Operator' },
  { value: 'api', label: 'API' },
];

const statusTone: Record<TraceContextStatus, 'info' | 'warning' | 'success' | 'error'> = {
  open: 'warning',
  completed: 'success',
  failed: 'error',
};

const timelineTone: Record<TraceTimelineEvent['kind'], string> = {
  query: 'info',
  approval: 'warning',
  execution: 'success',
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

export function TracesManager() {
  const [traces, setTraces] = useState<TraceContext[]>([]);
  const [statusFilter, setStatusFilter] = useState<TraceContextStatus | ''>('');
  const [sourceFilter, setSourceFilter] = useState<TraceContextSource | ''>('');
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<TraceContextDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  async function loadList() {
    setLoading(true);
    setLoadError(null);
    try {
      const query = new URLSearchParams();
      if (statusFilter) query.set('status', statusFilter);
      if (sourceFilter) query.set('source', sourceFilter);
      const suffix = query.toString() ? `?${query.toString()}` : '';
      const data = await apiRequest<TraceContext[]>(`/api/v1/traces${suffix}`);
      setTraces(data);
    } catch (error) {
      setLoadError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(traceId: string) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const data = await apiRequest<TraceContextDetail>(
        `/api/v1/traces/${encodeURIComponent(traceId)}`,
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
  }, [statusFilter, sourceFilter]);

  useEffect(() => {
    if (selectedId) {
      void loadDetail(selectedId);
    } else {
      setDetail(null);
    }
  }, [selectedId]);

  const summary = useMemo(() => {
    const totals = { open: 0, completed: 0, failed: 0 };
    for (const trace of traces) {
      totals[trace.status] += 1;
    }
    return totals;
  }, [traces]);

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h2>Traces</h2>
        <p className="muted">
          End-to-End Nachvollziehbarkeit jeder ABrain-Interaktion: Query → Actions → Approval → Execution →
          Result. Jede `trace_id` verknüpft Adapter-Response, Approval-Queue und Execution-Log.
        </p>
      </div>

      {loadError ? <InlineMessage tone="error">{loadError}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Übersicht">
          <div className="detailList">
            <div className="detailRow"><strong>Offen</strong><span>{summary.open}</span></div>
            <div className="detailRow"><strong>Abgeschlossen</strong><span>{summary.completed}</span></div>
            <div className="detailRow"><strong>Fehlgeschlagen</strong><span>{summary.failed}</span></div>
          </div>
        </Card>
        <Card title="Filter">
          <form className="entityForm" onSubmit={(event) => { event.preventDefault(); void loadList(); }}>
            <FormField label="Status">
              <select
                className="input"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as TraceContextStatus | '')}
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Quelle">
              <select
                className="input"
                value={sourceFilter}
                onChange={(event) => setSourceFilter(event.target.value as TraceContextSource | '')}
              >
                {SOURCE_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </FormField>
          </form>
        </Card>
        <Card title="Hinweis">
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            Traces enthalten nur einen kleinen Context-Snapshot — kein Event-Sourcing, keine Full-History.
            Für Details siehe Approvals und ABrain Execution Logs.
          </p>
        </Card>
      </div>

      <Card title="Traces">
        {loading ? (
          <InlineMessage>Lade Traces…</InlineMessage>
        ) : traces.length === 0 ? (
          <InlineMessage>Keine Traces für diesen Filter.</InlineMessage>
        ) : (
          <table className="dataTable">
            <thead>
              <tr>
                <th>Trace ID</th>
                <th>Quelle</th>
                <th>Status</th>
                <th>Query</th>
                <th>Approvals</th>
                <th>Executions</th>
                <th>Angelegt</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {traces.map((trace) => (
                <tr key={trace.trace_id}>
                  <td><code>{trace.trace_id}</code></td>
                  <td>{trace.source}</td>
                  <td>
                    <span className={`badge badge-${statusTone[trace.status]}`}>{trace.status}</span>
                  </td>
                  <td title={trace.root_query ?? ''}>
                    {trace.root_query ? trace.root_query.slice(0, 80) : '-'}
                  </td>
                  <td>
                    {trace.approval_count}
                    {trace.pending_approval_count > 0 ? ` (${trace.pending_approval_count} offen)` : ''}
                  </td>
                  <td>{trace.execution_count}</td>
                  <td>{formatTimestamp(trace.created_at)}</td>
                  <td>
                    <button
                      className="button buttonSecondary"
                      type="button"
                      onClick={() => setSelectedId(trace.trace_id)}
                    >
                      Timeline
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {selectedId ? (
        <Card title={`Trace · ${selectedId}`}>
          {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}
          {detailLoading ? (
            <InlineMessage>Lade Trace-Details…</InlineMessage>
          ) : detail ? (
            <div className="grid" style={{ gap: 16 }}>
              <div className="detailList">
                <div className="detailRow"><strong>Status</strong><span>{detail.status}</span></div>
                <div className="detailRow"><strong>Quelle</strong><span>{detail.source}</span></div>
                <div className="detailRow"><strong>Query</strong><span>{detail.root_query ?? '-'}</span></div>
                <div className="detailRow"><strong>Summary</strong><span>{detail.summary ?? '-'}</span></div>
                <div className="detailRow"><strong>Approvals</strong><span>{detail.approval_count} ({detail.pending_approval_count} offen)</span></div>
                <div className="detailRow"><strong>Executions</strong><span>{detail.execution_count}</span></div>
                <div className="detailRow"><strong>Angelegt</strong><span>{formatTimestamp(detail.created_at)}</span></div>
                <div className="detailRow"><strong>Aktualisiert</strong><span>{formatTimestamp(detail.updated_at)}</span></div>
              </div>

              <div>
                <h3>Timeline</h3>
                {detail.timeline.length === 0 ? (
                  <InlineMessage>Keine Timeline-Events.</InlineMessage>
                ) : (
                  <ol className="detailList" style={{ paddingLeft: 0, listStyle: 'none' }}>
                    {detail.timeline.map((event, index) => (
                      <li key={`${event.kind}-${index}`} className="detailRow">
                        <span>
                          <span className={`badge badge-${timelineTone[event.kind]}`}>{event.kind}</span>{' '}
                          <strong>{event.label}</strong>
                          {event.status ? <span className="muted"> · {event.status}</span> : null}
                        </span>
                        <span className="muted">{formatTimestamp(event.created_at)}</span>
                      </li>
                    ))}
                  </ol>
                )}
              </div>

              <div>
                <h3>Context-Snapshot</h3>
                <pre style={{ background: '#0b0f17', padding: 12, borderRadius: 8, overflow: 'auto', fontSize: '0.75rem' }}>
                  {JSON.stringify(detail.context_snapshot, null, 2)}
                </pre>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
