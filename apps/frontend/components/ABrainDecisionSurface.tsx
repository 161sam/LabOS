'use client';

import Link from 'next/link';
import { FormEvent, useCallback, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  ABrainAdapterContext,
  ABrainAdapterRecommendedAction,
  ABrainContextSection,
  ABrainExecutionResult,
  ABrainReasoningMode,
  ABrainReasoningResponse,
  abrainContextSectionOptions,
  abrainReasoningModeOptions,
} from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { ABrainRecommendationPanel } from './ABrainRecommendationPanel';
import { ABrainUseCaseSelector } from './ABrainUseCaseSelector';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unerwarteter Fehler';
}

function defaultQuestionFor(mode: ABrainReasoningMode): string {
  const option = abrainReasoningModeOptions.find((item) => item.value === mode);
  return option ? option.description : '';
}

type ABrainDecisionSurfaceProps = {
  initialMode?: ABrainReasoningMode;
};

export function ABrainDecisionSurface({ initialMode }: ABrainDecisionSurfaceProps = {}) {
  const { user } = useAuth();
  const canQuery = user?.role === 'admin';

  const [mode, setMode] = useState<ABrainReasoningMode>(initialMode ?? 'reactor_daily_overview');
  const [question, setQuestion] = useState<string>(defaultQuestionFor(initialMode ?? 'reactor_daily_overview'));
  const [sections, setSections] = useState<ABrainContextSection[]>([]);
  const [context, setContext] = useState<ABrainAdapterContext | null>(null);
  const [response, setResponse] = useState<ABrainReasoningResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [reasoning, setReasoning] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [executingKey, setExecutingKey] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<ABrainExecutionResult | null>(null);
  const [executionError, setExecutionError] = useState<string | null>(null);

  const loadContext = useCallback(async () => {
    setLoading(true);
    setPageError(null);
    try {
      const contextData = await apiRequest<ABrainAdapterContext>('/api/v1/abrain/adapter/context');
      setContext(contextData);
    } catch (error) {
      setPageError(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadContext();
  }, [loadContext]);

  function handleModeChange(next: ABrainReasoningMode) {
    setMode(next);
    setResponse(null);
    setQueryError(null);
    setExecutionResult(null);
    setExecutionError(null);
    setQuestion(defaultQuestionFor(next));
  }

  function toggleSection(section: ABrainContextSection) {
    setSections((current) =>
      current.includes(section) ? current.filter((item) => item !== section) : [...current, section],
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canQuery) {
      return;
    }
    setReasoning(true);
    setQueryError(null);
    setExecutionResult(null);
    setExecutionError(null);
    try {
      const result = await apiRequest<ABrainReasoningResponse>('/api/v1/abrain/adapter/reason', {
        method: 'POST',
        body: JSON.stringify({
          mode,
          question: question.trim() ? question.trim() : null,
          include_context_sections: sections.length > 0 ? sections : null,
          dry_run: true,
        }),
      });
      setResponse(result);
    } catch (error) {
      setQueryError(errorMessage(error));
    } finally {
      setReasoning(false);
    }
  }

  async function handleExecute(action: ABrainAdapterRecommendedAction, key: string) {
    if (!canQuery || !response) {
      return;
    }
    setExecutingKey(key);
    setExecutionError(null);
    setExecutionResult(null);
    try {
      const result = await apiRequest<ABrainExecutionResult>('/api/v1/abrain/execute', {
        method: 'POST',
        body: JSON.stringify({
          action: action.action,
          params: {},
          trace_id: response.trace_id,
          source: 'abrain',
          requested_via: 'adapter',
          reason: action.reason,
        }),
      });
      setExecutionResult(result);
    } catch (error) {
      setExecutionError(errorMessage(error));
    } finally {
      setExecutingKey(null);
    }
  }

  const activeOption = abrainReasoningModeOptions.find((item) => item.value === mode);

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>ABrain Decision Surface</h1>
        <p className="muted">
          LabOS nutzt die ABrain V2 Reasoning-Use-Cases. Reasoning bleibt in ABrain. Approval,
          Execution und Trace bleiben in LabOS sichtbar.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}

      <Card title="Use-Case auswaehlen">
        <ABrainUseCaseSelector value={mode} onChange={handleModeChange} disabled={loading} />
        {activeOption ? <p className="muted">{activeOption.description}</p> : null}
      </Card>

      <div className="grid cols-2">
        <Card title="ABrain befragen">
          {!canQuery ? (
            <InlineMessage>
              Reasoning-Abfragen sind nur fuer Admins freigegeben. Kontext und Status bleiben lesbar.
            </InlineMessage>
          ) : null}
          {queryError ? <InlineMessage tone="error">{queryError}</InlineMessage> : null}
          <form className="entityForm" onSubmit={handleSubmit}>
            <FormField label="Kontextbereiche (optional)">
              <div className="stackCompact">
                {abrainContextSectionOptions.map((option) => (
                  <label key={option.value} className="muted">
                    <input
                      type="checkbox"
                      checked={sections.includes(option.value)}
                      onChange={() => toggleSection(option.value)}
                      disabled={!canQuery}
                    />{' '}
                    {option.label}
                  </label>
                ))}
              </div>
            </FormField>
            <FormField label="Frage / Hinweis (optional)">
              <textarea
                className="input textarea"
                rows={3}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                disabled={!canQuery}
              />
            </FormField>
            <div className="buttonRow">
              <button className="button" type="submit" disabled={!canQuery || reasoning}>
                {reasoning ? 'Reasoning laeuft…' : 'ABrain V2 anstossen'}
              </button>
            </div>
          </form>
        </Card>

        <Card title="Lab-Kontext (Snapshot)">
          {loading ? (
            <InlineMessage>Lade Labor-Kontext…</InlineMessage>
          ) : context ? (
            <div className="detailList">
              <div className="detailRow">
                <strong>Offene Tasks</strong>
                <span>{context.summary.open_tasks}</span>
              </div>
              <div className="detailRow">
                <strong>Ueberfaellig</strong>
                <span>{context.summary.overdue_tasks}</span>
              </div>
              <div className="detailRow">
                <strong>Kritische Alerts</strong>
                <span>{context.summary.critical_alerts}</span>
              </div>
              <div className="detailRow">
                <strong>Offene Safety-Incidents</strong>
                <span>{context.operations.open_safety_incident_count}</span>
              </div>
              <div className="detailRow">
                <strong>Blockierte Commands</strong>
                <span>{context.operations.blocked_command_count}</span>
              </div>
              <div className="detailRow">
                <strong>Ueberfaellige Wartungen</strong>
                <span>{context.operations.overdue_maintenance_count}</span>
              </div>
              <div className="detailRow">
                <strong>Faellige Kalibrierungen</strong>
                <span>{context.operations.due_calibration_count}</span>
              </div>
              <div className="detailRow">
                <strong>Fehlgeschlagene Runs</strong>
                <span>{context.schedule.recent_failed_run_count}</span>
              </div>
            </div>
          ) : (
            <InlineMessage>Kein Labor-Kontext geladen.</InlineMessage>
          )}
        </Card>
      </div>

      {response ? (
        <div className="grid" style={{ gap: 24 }}>
          <Card title={`Reasoning-Ergebnis: ${activeOption?.label ?? response.reasoning_mode}`}>
            <div className="detailList">
              <div className="detailRow">
                <strong>Mode</strong>
                <span>{response.mode}</span>
              </div>
              <div className="detailRow">
                <strong>Fallback</strong>
                <span>{String(response.fallback_used)}</span>
              </div>
              <div className="detailRow">
                <strong>Policy</strong>
                <span>{response.policy_decision ?? '-'}</span>
              </div>
              <div className="detailRow">
                <strong>Trace</strong>
                <span>
                  {response.trace_id ? (
                    <Link href="/traces" title={response.trace_id}>
                      <code>{response.trace_id.slice(0, 12)}…</code>
                    </Link>
                  ) : (
                    '-'
                  )}
                </span>
              </div>
            </div>
            <p>
              <strong>Zusammenfassung:</strong> {response.summary}
            </p>
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
            {response.notes.length > 0 ? (
              <InlineMessage>{response.notes.join(' / ')}</InlineMessage>
            ) : null}
          </Card>

          {executionError ? <InlineMessage tone="error">{executionError}</InlineMessage> : null}
          {executionResult ? (
            <InlineMessage tone={executionResult.status === 'executed' ? undefined : 'warning'}>
              <span>
                Execution <strong>{executionResult.action}</strong>: {executionResult.status}
                {executionResult.blocked_reason ? ` (${executionResult.blocked_reason})` : ''}
                {executionResult.approval_request_id !== null ? (
                  <>
                    {' '}
                    ·{' '}
                    <Link href="/approvals">
                      Approval #{executionResult.approval_request_id}
                    </Link>
                  </>
                ) : null}
                {executionResult.log_id !== null ? (
                  <>
                    {' '}
                    · <Link href="/executions">Execution #{executionResult.log_id}</Link>
                  </>
                ) : null}
                {executionResult.trace_id ? (
                  <>
                    {' '}
                    ·{' '}
                    <Link href="/traces" title={executionResult.trace_id}>
                      Trace
                    </Link>
                  </>
                ) : null}
              </span>
            </InlineMessage>
          ) : null}

          <div className="grid cols-2">
            <Card title="Priorisierte Entitaeten">
              {response.prioritized_entities.length === 0 ? (
                <InlineMessage>Keine priorisierten Entitaeten.</InlineMessage>
              ) : (
                <ul>
                  {response.prioritized_entities.map((entity, index) => (
                    <li key={`${entity.entity_type}-${entity.entity_id ?? index}`}>
                      <strong>
                        {entity.entity_type}
                        {entity.entity_id !== null ? ` #${entity.entity_id}` : ''}
                      </strong>{' '}
                      — {entity.label}
                      {entity.severity ? (
                        <span className="badge badge-warning"> {entity.severity}</span>
                      ) : null}
                      {entity.reason ? <div className="muted">{entity.reason}</div> : null}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
            <Card title="Empfohlene Checks">
              {response.recommended_checks.length === 0 ? (
                <InlineMessage>Keine zusaetzlichen Checks empfohlen.</InlineMessage>
              ) : (
                <ul>
                  {response.recommended_checks.map((check, index) => (
                    <li key={`${check.check}-${index}`}>
                      <strong>{check.check}</strong>
                      {check.target ? <span className="muted"> → {check.target}</span> : null}
                      {check.reason ? <div className="muted">{check.reason}</div> : null}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>

          <Card title="Aktionen (Decision Surface)">
            <div className="stackBlock">
              <ABrainRecommendationPanel
                title="Empfohlene Aktionen"
                tone="recommend"
                items={response.recommended_actions}
                empty="Keine Aktion empfohlen."
                executingAction={executingKey}
                onExecute={canQuery ? (item) => handleExecute(item, `rec-${item.action}`) : undefined}
              />
              <ABrainRecommendationPanel
                title="Approval erforderlich"
                tone="approval"
                items={response.approval_required_actions}
                empty="Keine Approval-pflichtigen Aktionen."
                executingAction={executingKey}
                onExecute={canQuery ? (item) => handleExecute(item, `app-${item.action}`) : undefined}
              />
              <ABrainRecommendationPanel
                title="Blockiert / verschoben"
                tone="blocked"
                items={response.blocked_or_deferred_actions}
                empty="Keine blockierten oder verschobenen Aktionen."
              />
            </div>
          </Card>

          <Card title="Verwendete Kontextbereiche">
            {response.used_context_sections.length === 0 ? (
              <InlineMessage>Keine Kontextbereiche dokumentiert.</InlineMessage>
            ) : (
              <p className="muted">
                {response.used_context_sections.join(', ')} · ABrain entscheidet anhand dieser
                Snapshots. LabOS bleibt Quelle der Wahrheit.
              </p>
            )}
          </Card>
        </div>
      ) : null}
    </div>
  );
}
