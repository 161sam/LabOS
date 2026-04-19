'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  ABrainActionRiskLevel,
  ApprovalOverview,
  ApprovalRequest,
  ApprovalRequestStatus,
} from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const STATUS_FILTERS: Array<{ value: ApprovalRequestStatus | ''; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'pending', label: 'Offen' },
  { value: 'executed', label: 'Ausgeführt' },
  { value: 'failed', label: 'Fehlgeschlagen' },
  { value: 'rejected', label: 'Abgelehnt' },
  { value: 'cancelled', label: 'Cancelled' },
];

const riskTone: Record<ABrainActionRiskLevel, 'info' | 'warning' | 'error'> = {
  low: 'info',
  medium: 'warning',
  high: 'error',
  critical: 'error',
};

const statusTone: Record<ApprovalRequestStatus, 'info' | 'warning' | 'error' | 'success'> = {
  pending: 'warning',
  approved: 'info',
  rejected: 'info',
  executed: 'success',
  failed: 'error',
  cancelled: 'info',
};

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unerwarteter Fehler';
}

export function ApprovalsManager() {
  const { user } = useAuth();
  const canDecide = user?.role === 'admin' || user?.role === 'operator';

  const [overview, setOverview] = useState<ApprovalOverview | null>(null);
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [statusFilter, setStatusFilter] = useState<ApprovalRequestStatus | ''>('pending');
  const [traceFilter, setTraceFilter] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [decisionNote, setDecisionNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setLoadError(null);
    try {
      const query = new URLSearchParams();
      if (statusFilter) {
        query.set('status', statusFilter);
      }
      if (traceFilter.trim()) {
        query.set('trace_id', traceFilter.trim());
      }
      const suffix = query.toString() ? `?${query.toString()}` : '';
      const [ov, list] = await Promise.all([
        apiRequest<ApprovalOverview>('/api/v1/approvals/overview'),
        apiRequest<ApprovalRequest[]>(`/api/v1/approvals${suffix}`),
      ]);
      setOverview(ov);
      setRequests(list);
    } catch (error) {
      setLoadError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [statusFilter, traceFilter]);

  const selected = useMemo(
    () => requests.find((item) => item.id === selectedId) ?? null,
    [requests, selectedId],
  );

  async function decide(requestId: number, action: 'approve' | 'reject') {
    setBusy(true);
    setActionError(null);
    try {
      await apiRequest<ApprovalRequest>(`/api/v1/approvals/${requestId}/${action}`, {
        method: 'POST',
        body: JSON.stringify({ decision_note: decisionNote || null }),
      });
      setDecisionNote('');
      await load();
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  function handleFilterSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void load();
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h2>Approvals</h2>
        <p className="muted">
          HITL-Freigaben für approval-pflichtige ABrain-Aktionen. Freigabe ist kein Safety-Bypass — Safety- und Rollen-Guards
          werden bei der anschließenden Ausführung erneut geprüft.
        </p>
      </div>

      {loadError ? <InlineMessage tone="error">{loadError}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Offen">
          <div className="detailList">
            <div className="detailRow"><strong>Pending gesamt</strong><span>{overview?.pending ?? 0}</span></div>
            <div className="detailRow"><strong>Davon High-Risk</strong><span>{overview?.high_risk_pending ?? 0}</span></div>
          </div>
        </Card>
        <Card title="Entschieden">
          <div className="detailList">
            <div className="detailRow"><strong>Ausgeführt</strong><span>{overview?.executed ?? 0}</span></div>
            <div className="detailRow"><strong>Fehlgeschlagen</strong><span>{overview?.failed ?? 0}</span></div>
            <div className="detailRow"><strong>Abgelehnt</strong><span>{overview?.rejected ?? 0}</span></div>
          </div>
        </Card>
        <Card title="Filter">
          <form className="entityForm" onSubmit={handleFilterSubmit}>
            <FormField label="Status">
              <select
                className="input"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as ApprovalRequestStatus | '')}
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Trace-ID">
              <input
                className="input"
                value={traceFilter}
                onChange={(event) => setTraceFilter(event.target.value)}
                placeholder="labos-…"
              />
            </FormField>
          </form>
        </Card>
      </div>

      <Card title="Freigaben">
        {loading ? (
          <InlineMessage>Lade Approvals…</InlineMessage>
        ) : requests.length === 0 ? (
          <InlineMessage>Keine Einträge für diesen Filter.</InlineMessage>
        ) : (
          <table className="dataTable">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Risk</th>
                <th>Status</th>
                <th>Angefragt</th>
                <th>Trace</th>
                <th>Entscheider</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>
                    <code>{item.action_name}</code>
                  </td>
                  <td>
                    {item.risk_level ? (
                      <span className={`badge badge-${riskTone[item.risk_level]}`}>{item.risk_level}</span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    <span className={`badge badge-${statusTone[item.status]}`}>{item.status}</span>
                  </td>
                  <td>{item.requested_by_username ?? item.requested_by_source}</td>
                  <td>{item.trace_id ?? '-'}</td>
                  <td>{item.approved_by_username ?? '-'}</td>
                  <td>
                    <button
                      className="button buttonSecondary"
                      type="button"
                      onClick={() => setSelectedId(item.id)}
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {selected ? (
        <Card title={`Approval #${selected.id} — ${selected.action_name}`}>
          {actionError ? <InlineMessage tone="error">{actionError}</InlineMessage> : null}
          <div className="detailList">
            <div className="detailRow"><strong>Status</strong><span>{selected.status}</span></div>
            <div className="detailRow"><strong>Risk</strong><span>{selected.risk_level ?? '-'}</span></div>
            <div className="detailRow"><strong>Trace-ID</strong><span>{selected.trace_id ?? '-'}</span></div>
            <div className="detailRow"><strong>Quelle</strong><span>{selected.requested_by_source} ({selected.requested_via})</span></div>
            <div className="detailRow"><strong>Angefragt von</strong><span>{selected.requested_by_username ?? '-'}</span></div>
            <div className="detailRow"><strong>Begründung</strong><span>{selected.reason ?? '-'}</span></div>
            <div className="detailRow"><strong>Entschieden von</strong><span>{selected.approved_by_username ?? '-'}</span></div>
            <div className="detailRow"><strong>Decision Note</strong><span>{selected.decision_note ?? '-'}</span></div>
            <div className="detailRow"><strong>Execution Log</strong><span>{selected.executed_execution_log_id ?? '-'}</span></div>
            <div className="detailRow"><strong>Blocked Reason</strong><span>{selected.blocked_reason ?? '-'}</span></div>
            <div className="detailRow"><strong>Last Error</strong><span>{selected.last_error ?? '-'}</span></div>
          </div>
          <div>
            <strong>Parameter</strong>
            <pre className="codeBlock">{JSON.stringify(selected.action_params, null, 2)}</pre>
          </div>
          {selected.status === 'pending' ? (
            <div>
              {!canDecide ? (
                <InlineMessage>Nur Operator oder Admin können Freigaben entscheiden.</InlineMessage>
              ) : selected.risk_level && ['high', 'critical'].includes(selected.risk_level) && user?.role !== 'admin' ? (
                <InlineMessage tone="warning">High-Risk-Aktion — nur Admin darf genehmigen/ablehnen.</InlineMessage>
              ) : null}
              <FormField label="Decision Note (optional)">
                <textarea
                  className="input textarea"
                  rows={2}
                  value={decisionNote}
                  onChange={(event) => setDecisionNote(event.target.value)}
                  disabled={!canDecide || busy}
                />
              </FormField>
              <div className="buttonRow">
                <button
                  className="button"
                  type="button"
                  disabled={!canDecide || busy}
                  onClick={() => decide(selected.id, 'approve')}
                >
                  {busy ? 'Führe Freigabe aus…' : 'Freigeben & ausführen'}
                </button>
                <button
                  className="button buttonSecondary"
                  type="button"
                  disabled={!canDecide || busy}
                  onClick={() => decide(selected.id, 'reject')}
                >
                  Ablehnen
                </button>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
