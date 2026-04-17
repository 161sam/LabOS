'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Rule,
  RuleActionType,
  RuleConditionType,
  RuleEvaluationResponse,
  RuleExecution,
  RuleTriggerType,
  ruleActionTypeOptions,
  ruleConditionTypeOptions,
  ruleExecutionStatusOptions,
  ruleTriggerTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type RuleFormState = {
  name: string;
  description: string;
  is_enabled: boolean;
  trigger_type: RuleTriggerType;
  condition_type: RuleConditionType;
  condition_config: string;
  action_type: RuleActionType;
  action_config: string;
};

function createEmptyRuleForm(): RuleFormState {
  return {
    name: '',
    description: '',
    is_enabled: true,
    trigger_type: 'sensor_threshold',
    condition_type: 'threshold_gt',
    condition_config: '{\n  "sensor_id": 1,\n  "threshold": 23.5\n}',
    action_type: 'create_alert',
    action_config: '{\n  "title_template": "Automationsregel: {sensor_name} zu hoch",\n  "message_template": "Sensor {sensor_name} meldet {value} {unit}.",\n  "severity": "high",\n  "source_type": "sensor"\n}',
  };
}

function toRuleFormState(rule: Rule): RuleFormState {
  return {
    name: rule.name,
    description: rule.description ?? '',
    is_enabled: rule.is_enabled,
    trigger_type: rule.trigger_type,
    condition_type: rule.condition_type,
    condition_config: JSON.stringify(rule.condition_config, null, 2),
    action_type: rule.action_type,
    action_config: JSON.stringify(rule.action_config, null, 2),
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
    return 'Noch nie';
  }
  return new Date(value).toLocaleString('de-DE');
}

function badgeClass(tone: string) {
  return `badge badge-${tone}`;
}

function parseJsonField(value: string, fieldLabel: string) {
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`${fieldLabel} ist kein gueltiges JSON.`);
  }
}

export function RuleManager() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [executions, setExecutions] = useState<RuleExecution[]>([]);
  const [form, setForm] = useState<RuleFormState>(createEmptyRuleForm);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runningRuleId, setRunningRuleId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);

  async function loadData(preferredRuleId?: number | null) {
    setLoading(true);
    setPageError(null);
    try {
      const ruleData = await apiRequest<Rule[]>('/api/v1/rules');
      setRules(ruleData);
      const desiredRuleId =
        preferredRuleId && ruleData.some((rule) => rule.id === preferredRuleId)
          ? preferredRuleId
          : selectedRuleId && ruleData.some((rule) => rule.id === selectedRuleId)
            ? selectedRuleId
            : ruleData[0]?.id ?? null;
      setSelectedRuleId(desiredRuleId);
      if (desiredRuleId) {
        await loadExecutions(desiredRuleId);
      } else {
        setExecutions([]);
      }
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function loadExecutions(ruleId: number) {
    const data = await apiRequest<RuleExecution[]>(`/api/v1/rules/${ruleId}/executions?limit=10`);
    setExecutions(data);
  }

  function resetForm() {
    setMode('create');
    setEditingId(null);
    setForm(createEmptyRuleForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof RuleFormState>(key: Key, value: RuleFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function startEdit(ruleId: number) {
    setDetailLoading(true);
    setFormError(null);
    setNotice(null);
    try {
      const rule = await apiRequest<Rule>(`/api/v1/rules/${ruleId}`);
      setForm(toRuleFormState(rule));
      setMode('edit');
      setEditingId(rule.id);
      setSelectedRuleId(rule.id);
      await loadExecutions(rule.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    try {
      const payload = {
        name: form.name,
        description: form.description,
        is_enabled: form.is_enabled,
        trigger_type: form.trigger_type,
        condition_type: form.condition_type,
        condition_config: parseJsonField(form.condition_config, 'condition_config'),
        action_type: form.action_type,
        action_config: parseJsonField(form.action_config, 'action_config'),
      };

      if (mode === 'create') {
        const created = await apiRequest<Rule>('/api/v1/rules', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Regel angelegt.');
        resetForm();
        await loadData(created.id);
      } else if (editingId !== null) {
        const updated = await apiRequest<Rule>(`/api/v1/rules/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Regel aktualisiert.');
        resetForm();
        await loadData(updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleEnabled(rule: Rule) {
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<Rule>(`/api/v1/rules/${rule.id}/enabled`, {
        method: 'PATCH',
        body: JSON.stringify({ is_enabled: !rule.is_enabled }),
      });
      setNotice(`Regel ${rule.is_enabled ? 'deaktiviert' : 'aktiviert'}.`);
      await loadData(rule.id);
    } catch (error) {
      setPageError(getErrorMessage(error));
    }
  }

  async function evaluateRule(ruleId: number, dryRun: boolean) {
    setRunningRuleId(ruleId);
    setPageError(null);
    setNotice(null);
    try {
      const result = await apiRequest<RuleEvaluationResponse>(`/api/v1/rules/${ruleId}/evaluate?dry_run=${String(dryRun)}`, {
        method: 'POST',
      });
      setNotice(
        dryRun
          ? `Dry-Run fuer ${result.rule.name}: ${result.execution.status}`
          : `Ausfuehrung fuer ${result.rule.name}: ${result.execution.status}`,
      );
      await loadData(ruleId);
    } catch (error) {
      setPageError(getErrorMessage(error));
      await loadData(ruleId);
    } finally {
      setRunningRuleId(null);
    }
  }

  async function evaluateAllRules(dryRun: boolean) {
    setRunningRuleId(-1);
    setPageError(null);
    setNotice(null);
    try {
      const result = await apiRequest<{ executions: RuleExecution[] }>(`/api/v1/rules/evaluate-all?dry_run=${String(dryRun)}`, {
        method: 'POST',
      });
      setNotice(`${result.executions.length} Regeln ${dryRun ? 'im Dry-Run' : 'echt'} evaluiert.`);
      await loadData(selectedRuleId);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setRunningRuleId(null);
    }
  }

  const selectedRule = rules.find((rule) => rule.id === selectedRuleId) ?? null;

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Automation</h1>
        <p className="muted">Kontrollierte Regeln evaluieren, Dry-Runs ausfuehren und nachvollziehbare Task- oder Alert-Aktionen protokollieren.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="buttonRow">
        <button className="button buttonSecondary" type="button" disabled={runningRuleId !== null} onClick={() => void evaluateAllRules(true)}>
          Alle Regeln Dry-Run
        </button>
        <button className="button buttonSecondary" type="button" disabled={runningRuleId !== null} onClick={() => void evaluateAllRules(false)}>
          Alle Regeln ausfuehren
        </button>
      </div>

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neue Regel' : `Regel bearbeiten #${editingId}`}>
          {detailLoading ? <InlineMessage>Lade Regel…</InlineMessage> : null}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Name">
                <input className="input" value={form.name} onChange={(event) => setFormValue('name', event.target.value)} required />
              </FormField>

              <FormField label="Aktiv">
                <select className="input" value={String(form.is_enabled)} onChange={(event) => setFormValue('is_enabled', event.target.value === 'true')}>
                  <option value="true">Aktiv</option>
                  <option value="false">Inaktiv</option>
                </select>
              </FormField>

              <FormField label="Trigger">
                <select className="input" value={form.trigger_type} onChange={(event) => setFormValue('trigger_type', event.target.value as RuleTriggerType)}>
                  {ruleTriggerTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Condition">
                <select className="input" value={form.condition_type} onChange={(event) => setFormValue('condition_type', event.target.value as RuleConditionType)}>
                  {ruleConditionTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Action">
                <select className="input" value={form.action_type} onChange={(event) => setFormValue('action_type', event.target.value as RuleActionType)}>
                  {ruleActionTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>

            <FormField label="Beschreibung">
              <textarea className="input textarea" rows={3} value={form.description} onChange={(event) => setFormValue('description', event.target.value)} />
            </FormField>

            <FormField label="condition_config (JSON)">
              <textarea className="input textarea" rows={8} value={form.condition_config} onChange={(event) => setFormValue('condition_config', event.target.value)} />
            </FormField>

            <FormField label="action_config (JSON)">
              <textarea className="input textarea" rows={8} value={form.action_config} onChange={(event) => setFormValue('action_config', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Regel anlegen' : 'Regel speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Regeln">
          {loading ? (
            <InlineMessage>Lade Regeln…</InlineMessage>
          ) : rules.length === 0 ? (
            <InlineMessage>Noch keine Regeln vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Trigger</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Zuletzt evaluiert</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule) => (
                    <tr key={rule.id}>
                      <td>
                        <div className="stackCompact">
                          <strong>{rule.name}</strong>
                          <span className="muted">{rule.description || 'Ohne Beschreibung'}</span>
                        </div>
                      </td>
                      <td>{rule.trigger_type}</td>
                      <td>{rule.action_type}</td>
                      <td>
                        <span className={badgeClass(rule.is_enabled ? 'done' : 'warning')}>
                          {rule.is_enabled ? 'aktiv' : 'inaktiv'}
                        </span>
                      </td>
                      <td>{formatDateTime(rule.last_evaluated_at)}</td>
                      <td>
                        <div className="buttonRow">
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(rule.id)}>
                            Bearbeiten
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void toggleEnabled(rule)}>
                            {rule.is_enabled ? 'Deaktivieren' : 'Aktivieren'}
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" disabled={runningRuleId !== null} onClick={() => void evaluateRule(rule.id, true)}>
                            Dry-Run
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" disabled={runningRuleId !== null} onClick={() => void evaluateRule(rule.id, false)}>
                            Ausfuehren
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

      <Card title={selectedRule ? `Letzte Ausfuehrungen: ${selectedRule.name}` : 'Letzte Ausfuehrungen'}>
        {!selectedRule ? (
          <InlineMessage>Waehle oder evaluiere eine Regel, um das Execution-Log zu sehen.</InlineMessage>
        ) : executions.length === 0 ? (
          <InlineMessage>Fuer diese Regel gibt es noch keine Ausfuehrungen.</InlineMessage>
        ) : (
          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Dry-Run</th>
                  <th>Evaluation</th>
                  <th>Action Result</th>
                  <th>Zeitpunkt</th>
                </tr>
              </thead>
              <tbody>
                {executions.map((execution) => (
                  <tr key={execution.id}>
                    <td><span className={badgeClass(execution.status)}>{ruleExecutionStatusOptions.find((item) => item.value === execution.status)?.label ?? execution.status}</span></td>
                    <td>{execution.dry_run ? 'Ja' : 'Nein'}</td>
                    <td><pre>{JSON.stringify(execution.evaluation_summary, null, 2)}</pre></td>
                    <td><pre>{JSON.stringify(execution.action_result, null, 2)}</pre></td>
                    <td>{formatDateTime(execution.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
