'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  ABrainContext,
  ABrainContextSection,
  ABrainPreset,
  ABrainPresetDefinition,
  ABrainQueryResponse,
  ABrainStatus,
  abrainContextSectionOptions,
  abrainPresetOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type QueryFormState = {
  question: string;
  preset: string;
  include_context_sections: ABrainContextSection[];
};

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function createEmptyForm(): QueryFormState {
  return {
    question: '',
    preset: 'daily_overview',
    include_context_sections: [],
  };
}

function formatDateTime(value: string | null) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

export function ABrainAssistant() {
  const [status, setStatus] = useState<ABrainStatus | null>(null);
  const [presets, setPresets] = useState<ABrainPresetDefinition[]>([]);
  const [context, setContext] = useState<ABrainContext | null>(null);
  const [response, setResponse] = useState<ABrainQueryResponse | null>(null);
  const [form, setForm] = useState<QueryFormState>(createEmptyForm);
  const [loading, setLoading] = useState(true);
  const [queryLoading, setQueryLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  async function loadData(preselectedPreset?: string) {
    setLoading(true);
    setPageError(null);

    try {
      const [statusData, presetData, contextData] = await Promise.all([
        apiRequest<ABrainStatus>('/api/v1/abrain/status'),
        apiRequest<ABrainPresetDefinition[]>('/api/v1/abrain/presets'),
        apiRequest<ABrainContext>('/api/v1/abrain/context'),
      ]);
      setStatus(statusData);
      setPresets(presetData);
      setContext(contextData);

      const activePreset = presetData.find((item) => item.id === (preselectedPreset ?? form.preset)) ?? presetData[0];
      if (activePreset) {
        setForm((current) => ({
          ...current,
          preset: activePreset.id,
          question: current.question || activePreset.default_question,
          include_context_sections:
            current.include_context_sections.length > 0 ? current.include_context_sections : activePreset.default_sections,
        }));
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

  function setFormValue<Key extends keyof QueryFormState>(key: Key, value: QueryFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function toggleSection(section: ABrainContextSection) {
    setForm((current) => ({
      ...current,
      include_context_sections: current.include_context_sections.includes(section)
        ? current.include_context_sections.filter((item) => item !== section)
        : [...current.include_context_sections, section],
    }));
  }

  function applyPreset(presetId: ABrainPreset) {
    const preset = presets.find((item) => item.id === presetId);
    if (!preset) {
      return;
    }
    setForm({
      question: preset.default_question,
      preset: preset.id,
      include_context_sections: preset.default_sections,
    });
    setResponse(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setQueryLoading(true);
    setQueryError(null);

    try {
      const result = await apiRequest<ABrainQueryResponse>('/api/v1/abrain/query', {
        method: 'POST',
        body: JSON.stringify({
          question: form.question,
          preset: form.preset || null,
          include_context_sections:
            form.include_context_sections.length > 0 ? form.include_context_sections : undefined,
        }),
      });
      setResponse(result);
      await loadContextOnly(result.used_context_sections);
    } catch (error) {
      setQueryError(getErrorMessage(error));
    } finally {
      setQueryLoading(false);
    }
  }

  async function loadContextOnly(includeSections: ABrainContextSection[]) {
    const params = new URLSearchParams();
    includeSections.forEach((section) => params.append('include_sections', section));
    const path = params.size > 0 ? `/api/v1/abrain/context?${params.toString()}` : '/api/v1/abrain/context';
    try {
      const contextData = await apiRequest<ABrainContext>(path);
      setContext(contextData);
    } catch {
      // Keep previous context visible if refresh fails.
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>ABrain</h1>
        <p className="muted">Datenbasierte Labor-Assistenz auf Basis echter LabOS-Kontextdaten, ohne automatische Ausfuehrung.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="Assistenz anfragen">
          {queryError ? <InlineMessage tone="error">{queryError}</InlineMessage> : null}

          <div className="buttonRow" style={{ marginBottom: 16 }}>
            {abrainPresetOptions.map((option) => (
              <button
                key={option.value}
                className="button buttonSecondary buttonCompact"
                type="button"
                onClick={() => applyPreset(option.value)}
                disabled={loading}
              >
                {option.label}
              </button>
            ))}
          </div>

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Preset">
                <select
                  className="input"
                  value={form.preset}
                  onChange={(event) => applyPreset(event.target.value as ABrainPreset)}
                >
                  {presets.map((preset) => (
                    <option key={preset.id} value={preset.id}>
                      {preset.title}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Kontextbereiche">
                <div className="stackCompact">
                  {abrainContextSectionOptions.map((option) => (
                    <label key={option.value} className="muted">
                      <input
                        type="checkbox"
                        checked={form.include_context_sections.includes(option.value)}
                        onChange={() => toggleSection(option.value)}
                      />{' '}
                      {option.label}
                    </label>
                  ))}
                </div>
              </FormField>
            </div>

            <FormField label="Frage">
              <textarea
                className="input textarea"
                rows={5}
                value={form.question}
                onChange={(event) => setFormValue('question', event.target.value)}
                required
              />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={queryLoading || loading}>
                {queryLoading ? 'Analysiert…' : 'ABrain befragen'}
              </button>
            </div>
          </form>
        </Card>

        <Card title="Status und Kontext">
          {loading ? (
            <InlineMessage>Lade ABrain-Kontext…</InlineMessage>
          ) : (
            <div className="stackBlock">
              {status ? (
                <div className="detailList">
                  <div className="detailRow"><strong>Modus</strong><span>{status.mode}</span></div>
                  <div className="detailRow"><strong>Verbunden</strong><span>{String(status.connected)}</span></div>
                  <div className="detailRow"><strong>Fallback</strong><span>{String(status.fallback_available)}</span></div>
                  <div className="detailRow"><strong>Timeout</strong><span>{status.timeout_seconds}s</span></div>
                </div>
              ) : null}

              {status ? <InlineMessage>{status.note}</InlineMessage> : null}

              {context ? (
                <div className="grid cols-3">
                  <Card title="Offene Tasks"><div className="kpi">{context.summary.open_tasks}</div></Card>
                  <Card title="Kritische Alerts"><div className="kpi">{context.summary.critical_alerts}</div></Card>
                  <Card title="Sensor Attention"><div className="kpi">{context.summary.sensor_attention}</div></Card>
                </div>
              ) : null}
            </div>
          )}
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title="Antwort">
          {!response ? (
            <InlineMessage>Noch keine Analyse ausgefuehrt.</InlineMessage>
          ) : (
            <div className="stackBlock">
              <p><strong>Zusammenfassung:</strong> {response.summary}</p>
              <div>
                <strong>Highlights</strong>
                <ul>
                  {response.highlights.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <strong>Empfohlene Aktionen</strong>
                <ul>
                  {response.recommended_actions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <p className="muted">
                Verwendete Kontextbereiche: {response.used_context_sections.join(', ')}
              </p>
              {response.note ? <InlineMessage>{response.note}</InlineMessage> : null}
            </div>
          )}
        </Card>

        <Card title="Nachvollziehbare Datengrundlage">
          {!context ? (
            <InlineMessage>Kein Kontext geladen.</InlineMessage>
          ) : (
            <div className="stackBlock">
              <p className="muted">Generiert am {formatDateTime(context.generated_at)}</p>

              {context.tasks && context.tasks.length > 0 ? (
                <div>
                  <strong>Tasks</strong>
                  <ul>
                    {context.tasks.map((task) => (
                      <li key={`task-${task.id}`}>
                        {task.title} ({task.priority}, {task.status})
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {context.alerts && context.alerts.length > 0 ? (
                <div>
                  <strong>Alerts</strong>
                  <ul>
                    {context.alerts.map((alert) => (
                      <li key={`alert-${alert.id}`}>
                        {alert.title} ({alert.severity}, {alert.status})
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {context.sensors && context.sensors.length > 0 ? (
                <div>
                  <strong>Sensoren</strong>
                  <ul>
                    {context.sensors.map((sensor) => (
                      <li key={`sensor-${sensor.id}`}>
                        {sensor.name}: {sensor.attention_reason}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {context.reactors && context.reactors.length > 0 ? (
                <div>
                  <strong>Reaktoren</strong>
                  <ul>
                    {context.reactors.map((reactor) => (
                      <li key={`reactor-${reactor.id}`}>
                        {reactor.name}: {reactor.status}, offene Tasks {reactor.open_task_count}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {context.photos && context.photos.length > 0 ? (
                <div>
                  <strong>Letzte Fotos</strong>
                  <ul>
                    {context.photos.map((photo) => (
                      <li key={`photo-${photo.id}`}>
                        {photo.title || `Foto #${photo.id}`} ({formatDateTime(photo.captured_at || photo.created_at)})
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {response?.referenced_entities.length ? (
                <div>
                  <strong>Referenzierte Objekte</strong>
                  <ul>
                    {response.referenced_entities.map((reference) => (
                      <li key={`${reference.entity_type}-${reference.entity_id}`}>
                        {reference.entity_type} #{reference.entity_id}: {reference.label}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
