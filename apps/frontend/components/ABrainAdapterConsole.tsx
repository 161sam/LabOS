'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  ABrainActionCatalog,
  ABrainActionDescriptor,
  ABrainActionRiskLevel,
  ABrainAdapterContext,
  ABrainAdapterRecommendedAction,
  ABrainAdapterResponse,
  ABrainPreset,
  abrainPresetOptions,
} from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const riskTone: Record<ABrainActionRiskLevel, 'info' | 'warning' | 'error'> = {
  low: 'info',
  medium: 'warning',
  high: 'error',
  critical: 'error',
};

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unerwarteter Fehler';
}

export function ABrainAdapterConsole() {
  const { user } = useAuth();
  const canQuery = user?.role === 'admin';

  const [catalog, setCatalog] = useState<ABrainActionCatalog | null>(null);
  const [context, setContext] = useState<ABrainAdapterContext | null>(null);
  const [response, setResponse] = useState<ABrainAdapterResponse | null>(null);
  const [question, setQuestion] = useState('Was sollte ich jetzt anschauen?');
  const [preset, setPreset] = useState<ABrainPreset | ''>('critical_issues');
  const [loading, setLoading] = useState(true);
  const [queryLoading, setQueryLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  async function loadAdapterData() {
    setLoading(true);
    setLoadError(null);
    try {
      const [catalogData, contextData] = await Promise.all([
        apiRequest<ABrainActionCatalog>('/api/v1/abrain/actions'),
        apiRequest<ABrainAdapterContext>('/api/v1/abrain/adapter/context'),
      ]);
      setCatalog(catalogData);
      setContext(contextData);
    } catch (error) {
      setLoadError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAdapterData();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canQuery) {
      return;
    }
    setQueryLoading(true);
    setQueryError(null);
    try {
      const result = await apiRequest<ABrainAdapterResponse>('/api/v1/abrain/adapter/query', {
        method: 'POST',
        body: JSON.stringify({
          question,
          preset: preset ? preset : null,
          dry_run: true,
        }),
      });
      setResponse(result);
      await loadAdapterData();
    } catch (error) {
      setQueryError(errorMessage(error));
    } finally {
      setQueryLoading(false);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h2>ABrain Adapter Console</h2>
        <p className="muted">
          Steuerungs- und Entscheidungsansicht fuer den LabOS-Adapter: statische Tool-Surface,
          strukturierter Kontext und Empfehlungen mit expliziter Genehmigungsanforderung.
        </p>
      </div>

      {loadError ? <InlineMessage tone="error">{loadError}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Adapter Modus">
          {context ? (
            <div className="detailList">
              <div className="detailRow"><strong>Mode</strong><span>{context.mode}</span></div>
              <div className="detailRow"><strong>Fallback aktiv</strong><span>{String(context.fallback_used)}</span></div>
              <div className="detailRow"><strong>Contract</strong><span>{context.contract_version}</span></div>
              <div className="detailRow"><strong>Generiert</strong><span>{new Date(context.generated_at).toLocaleString('de-DE')}</span></div>
            </div>
          ) : (
            <InlineMessage>{loading ? 'Lade Adapter-Kontext…' : 'Kein Adapter-Kontext verfuegbar.'}</InlineMessage>
          )}
        </Card>
        <Card title="Offene Safety / Maintenance">
          {context ? (
            <div className="detailList">
              <div className="detailRow"><strong>Safety Incidents</strong><span>{context.operations.open_safety_incident_count}</span></div>
              <div className="detailRow"><strong>Blockierte Commands</strong><span>{context.operations.blocked_command_count}</span></div>
              <div className="detailRow"><strong>Fehlgeschlagen</strong><span>{context.operations.failed_command_count}</span></div>
              <div className="detailRow"><strong>Kalibrierung faellig</strong><span>{context.operations.due_calibration_count}</span></div>
              <div className="detailRow"><strong>Wartung ueberfaellig</strong><span>{context.operations.overdue_maintenance_count}</span></div>
            </div>
          ) : null}
        </Card>
        <Card title="Resourcen">
          {context ? (
            <div className="detailList">
              <div className="detailRow"><strong>Inventar kritisch</strong><span>{context.resources.out_of_stock.length + context.resources.low_stock.length}</span></div>
              <div className="detailRow"><strong>Assets Attention</strong><span>{context.resources.assets_attention.length}</span></div>
              <div className="detailRow"><strong>Nodes offline</strong><span>{context.resources.offline_nodes.length}</span></div>
              <div className="detailRow"><strong>Aktive Schedules</strong><span>{context.schedule.active_schedule_count}</span></div>
              <div className="detailRow"><strong>Recent Failed Runs</strong><span>{context.schedule.recent_failed_run_count}</span></div>
            </div>
          ) : null}
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title="Adapter-Query (dry_run)">
          {!canQuery ? (
            <InlineMessage>Adapter-Abfragen sind nur fuer Admins freigegeben. Kontext und Katalog bleiben lesbar.</InlineMessage>
          ) : null}
          {queryError ? <InlineMessage tone="error">{queryError}</InlineMessage> : null}
          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Preset">
                <select
                  className="input"
                  value={preset}
                  onChange={(event) => setPreset(event.target.value as ABrainPreset | '')}
                  disabled={!canQuery}
                >
                  <option value="">(ohne Preset)</option>
                  {abrainPresetOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>
            <FormField label="Frage">
              <textarea
                className="input textarea"
                rows={3}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                required
                disabled={!canQuery}
              />
            </FormField>
            <div className="buttonRow">
              <button className="button" type="submit" disabled={!canQuery || queryLoading}>
                {queryLoading ? 'Adapter laeuft…' : 'Adapter befragen'}
              </button>
            </div>
          </form>
        </Card>

        <Card title="Antwort & Empfehlungen">
          {!response ? (
            <InlineMessage>Noch keine Adapter-Antwort.</InlineMessage>
          ) : (
            <div className="stackBlock">
              <div className="detailList">
                <div className="detailRow"><strong>Mode</strong><span>{response.mode}</span></div>
                <div className="detailRow"><strong>Fallback</strong><span>{String(response.fallback_used)}</span></div>
                <div className="detailRow"><strong>Policy</strong><span>{response.policy_decision ?? '-'}</span></div>
                <div className="detailRow"><strong>Approval required</strong><span>{String(response.approval_required)}</span></div>
                <div className="detailRow"><strong>Trace</strong><span>{response.trace_id ?? '-'}</span></div>
              </div>
              <p><strong>Zusammenfassung:</strong> {response.summary}</p>
              {response.highlights.length > 0 ? (
                <div>
                  <strong>Highlights</strong>
                  <ul>
                    {response.highlights.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <RecommendationList title="Empfohlene Aktionen" items={response.recommended_actions} empty="Keine Aktion empfohlen." />
              <RecommendationList
                title="Blockierte Aktionen"
                items={response.blocked_actions}
                empty="Keine blockierten Aktionen."
                tone="error"
              />
              {response.notes.length > 0 ? (
                <InlineMessage>{response.notes.join(' / ')}</InlineMessage>
              ) : null}
            </div>
          )}
        </Card>
      </div>

      <Card title="Action Catalog (Tool Surface V1)">
        {catalog ? (
          <div className="stackBlock">
            <p className="muted">Contract {catalog.contract_version} - {catalog.actions.length} Aktionen</p>
            <table className="table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Domain</th>
                  <th>Risk</th>
                  <th>Approval</th>
                  <th>Guards</th>
                </tr>
              </thead>
              <tbody>
                {catalog.actions.map((action) => (
                  <CatalogRow key={action.name} action={action} />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <InlineMessage>{loading ? 'Lade Katalog…' : 'Kein Katalog geladen.'}</InlineMessage>
        )}
      </Card>
    </div>
  );
}

function CatalogRow({ action }: { action: ABrainActionDescriptor }) {
  return (
    <tr>
      <td>
        <strong>{action.name}</strong>
        <div className="muted">{action.description}</div>
      </td>
      <td>{action.domain}</td>
      <td>
        <span className={`badge badge-${riskTone[action.risk_level]}`}>{action.risk_level}</span>
      </td>
      <td>{action.requires_approval ? 'required' : 'auto'}</td>
      <td className="muted">{action.guarded_by.length > 0 ? action.guarded_by.join(', ') : '-'}</td>
    </tr>
  );
}

function RecommendationList({
  title,
  items,
  empty,
  tone,
}: {
  title: string;
  items: ABrainAdapterRecommendedAction[];
  empty: string;
  tone?: 'error';
}) {
  if (items.length === 0) {
    return (
      <div>
        <strong>{title}</strong>
        <InlineMessage tone={tone}>{empty}</InlineMessage>
      </div>
    );
  }
  return (
    <div>
      <strong>{title}</strong>
      <ul>
        {items.map((item, index) => (
          <li key={`${item.action}-${index}`}>
            <strong>{item.action}</strong>{item.target ? ` -> ${item.target}` : ''}{' '}
            <span className={`badge badge-${riskTone[item.risk_level]}`}>{item.risk_level}</span>{' '}
            {item.requires_approval ? <span className="badge badge-warning">approval</span> : null}{' '}
            {item.blocked ? <span className="badge badge-error">blocked{item.blocked_reason ? `: ${item.blocked_reason}` : ''}</span> : null}
            <div className="muted">{item.reason}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
