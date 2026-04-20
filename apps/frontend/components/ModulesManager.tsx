'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  AutonomousModule,
  AutonomousModuleDetail,
  AutonomousModuleOverview,
  ModuleAutonomyLevel,
  ModuleCapabilityType,
  ModuleStatus,
  ModuleType,
  moduleAutonomyLevelOptions,
  moduleCapabilityTypeOptions,
  moduleStatusOptions,
  moduleTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type ModuleFormState = {
  module_id: string;
  name: string;
  module_type: ModuleType;
  status: ModuleStatus;
  autonomy_level: ModuleAutonomyLevel;
  reactor_id: string;
  asset_id: string;
  device_node_id: string;
  zone: string;
  location: string;
  description: string;
  ros_node_name: string;
  mqtt_node_id: string;
  wiki_ref: string;
  capabilities: ModuleCapabilityType[];
};

type ModuleFilters = {
  module_type: string;
  status: string;
  autonomy_level: string;
  zone: string;
};

function createEmptyForm(): ModuleFormState {
  return {
    module_id: '',
    name: '',
    module_type: 'reactor',
    status: 'nominal',
    autonomy_level: 'manual',
    reactor_id: '',
    asset_id: '',
    device_node_id: '',
    zone: '',
    location: '',
    description: '',
    ros_node_name: '',
    mqtt_node_id: '',
    wiki_ref: '',
    capabilities: [],
  };
}

function createEmptyFilters(): ModuleFilters {
  return { module_type: '', status: '', autonomy_level: '', zone: '' };
}

function toFormState(detail: AutonomousModuleDetail): ModuleFormState {
  return {
    module_id: detail.module_id,
    name: detail.name,
    module_type: detail.module_type,
    status: detail.status,
    autonomy_level: detail.autonomy_level,
    reactor_id: detail.reactor_id !== null ? String(detail.reactor_id) : '',
    asset_id: detail.asset_id !== null ? String(detail.asset_id) : '',
    device_node_id: detail.device_node_id !== null ? String(detail.device_node_id) : '',
    zone: detail.zone ?? '',
    location: detail.location ?? '',
    description: detail.description ?? '',
    ros_node_name: detail.ros_node_name ?? '',
    mqtt_node_id: detail.mqtt_node_id ?? '',
    wiki_ref: detail.wiki_ref ?? '',
    capabilities: detail.capabilities.map((capability) => capability.capability_type),
  };
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

function badgeClass(tone: string) {
  return `badge badge-${tone}`;
}

function getLabel<T extends string>(
  options: ReadonlyArray<{ value: T; label: string }>,
  value: T,
): string {
  return options.find((option) => option.value === value)?.label ?? value;
}

function parseOptionalId(value: string): number | null {
  if (!value) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function ModulesManager() {
  const [modules, setModules] = useState<AutonomousModule[]>([]);
  const [overview, setOverview] = useState<AutonomousModuleOverview | null>(null);
  const [selected, setSelected] = useState<AutonomousModuleDetail | null>(null);
  const [filters, setFilters] = useState<ModuleFilters>(createEmptyFilters);
  const [form, setForm] = useState<ModuleFormState>(createEmptyForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, ModuleStatus>>({});
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusSavingId, setStatusSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  async function fetchDetail(moduleId: number) {
    const detail = await apiRequest<AutonomousModuleDetail>(`/api/v1/modules/${moduleId}`);
    setSelected(detail);
    return detail;
  }

  async function loadData(nextFilters: ModuleFilters = filters, preferredId?: number | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.module_type) params.set('module_type', nextFilters.module_type);
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.autonomy_level) params.set('autonomy_level', nextFilters.autonomy_level);
    if (nextFilters.zone) params.set('zone', nextFilters.zone);
    const path = params.size > 0 ? `/api/v1/modules?${params.toString()}` : '/api/v1/modules';

    try {
      const [list, overviewData] = await Promise.all([
        apiRequest<AutonomousModule[]>(path),
        apiRequest<AutonomousModuleOverview>('/api/v1/modules/overview'),
      ]);
      setModules(list);
      setOverview(overviewData);
      setStatusDrafts(
        Object.fromEntries(list.map((module) => [module.id, module.status])) as Record<number, ModuleStatus>,
      );

      if (list.length === 0) {
        setSelected(null);
        if (mode !== 'edit') {
          setForm(createEmptyForm());
        }
        return;
      }

      const desiredId =
        preferredId && list.some((module) => module.id === preferredId)
          ? preferredId
          : selected && list.some((module) => module.id === selected.id)
            ? selected.id
            : list[0].id;

      await fetchDetail(desiredId);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData(filters);
  }, []);

  function resetForm() {
    setMode('create');
    setEditingId(null);
    setForm(createEmptyForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof ModuleFormState>(key: Key, value: ModuleFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function toggleCapability(capability: ModuleCapabilityType) {
    setForm((current) => {
      const exists = current.capabilities.includes(capability);
      return {
        ...current,
        capabilities: exists
          ? current.capabilities.filter((item) => item !== capability)
          : [...current.capabilities, capability],
      };
    });
  }

  function setFilterValue<Key extends keyof ModuleFilters>(key: Key, value: ModuleFilters[Key]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  async function selectModule(moduleId: number) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      await fetchDetail(moduleId);
    } catch (error) {
      setDetailError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  async function startEdit(moduleId: number) {
    setDetailLoading(true);
    setFormError(null);
    try {
      const detail = await fetchDetail(moduleId);
      setForm(toFormState(detail));
      setMode('edit');
      setEditingId(detail.id);
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

    const payload = {
      module_id: form.module_id,
      name: form.name,
      module_type: form.module_type,
      status: form.status,
      autonomy_level: form.autonomy_level,
      reactor_id: parseOptionalId(form.reactor_id),
      asset_id: parseOptionalId(form.asset_id),
      device_node_id: parseOptionalId(form.device_node_id),
      zone: form.zone || null,
      location: form.location || null,
      description: form.description || null,
      ros_node_name: form.ros_node_name || null,
      mqtt_node_id: form.mqtt_node_id || null,
      wiki_ref: form.wiki_ref || null,
    };

    try {
      if (mode === 'create') {
        const created = await apiRequest<AutonomousModuleDetail>('/api/v1/modules', {
          method: 'POST',
          body: JSON.stringify({
            ...payload,
            capabilities: form.capabilities.map((capability_type) => ({
              capability_type,
              is_enabled: true,
            })),
          }),
        });
        setNotice('Modul angelegt.');
        resetForm();
        await loadData(filters, created.id);
      } else if (editingId !== null) {
        const updated = await apiRequest<AutonomousModuleDetail>(`/api/v1/modules/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        await apiRequest<unknown>(`/api/v1/modules/${editingId}/capabilities`, {
          method: 'PUT',
          body: JSON.stringify(
            form.capabilities.map((capability_type) => ({
              capability_type,
              is_enabled: true,
            })),
          ),
        });
        setNotice('Modul aktualisiert.');
        resetForm();
        await loadData(filters, updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(module: AutonomousModule) {
    const nextStatus = statusDrafts[module.id] ?? module.status;
    if (nextStatus === module.status) {
      return;
    }
    setStatusSavingId(module.id);
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<AutonomousModuleDetail>(`/api/v1/modules/${module.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      setNotice(`Status von ${module.name} aktualisiert.`);
      await loadData(filters, module.id);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setStatusSavingId(null);
    }
  }

  async function handleFilterSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadData(filters);
  }

  async function resetFilters() {
    const empty = createEmptyFilters();
    setFilters(empty);
    await loadData(empty);
  }

  const byTypeEntries = useMemo(() => {
    if (!overview) return [];
    return Object.entries(overview.by_type).sort(([a], [b]) => a.localeCompare(b));
  }, [overview]);

  const byAutonomyEntries = useMemo(() => {
    if (!overview) return [];
    return Object.entries(overview.by_autonomy_level).sort(([a], [b]) => a.localeCompare(b));
  }, [overview]);

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>RobotOps — Autonome Module</h1>
        <p className="muted">
          Reaktoren, Hydroponik, Sampling, Vision und Werkstatt-Systeme als robotische Einheiten.
          LabOS bleibt Source of Truth; Execution/Safety/Approval laufen weiterhin ueber die
          bestehenden Pipelines.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-4">
        <Card title="Module gesamt"><div className="kpi">{overview?.total_modules ?? 0}</div></Card>
        <Card title="Nominal"><div className="kpi">{overview?.nominal_modules ?? 0}</div></Card>
        <Card title="Warnungen"><div className="kpi">{(overview?.warning_modules ?? 0) + (overview?.attention_modules ?? 0)}</div></Card>
        <Card title="Incidents / Offline"><div className="kpi">{(overview?.incident_modules ?? 0) + (overview?.offline_modules ?? 0)}</div></Card>
      </div>

      <div className="grid cols-2">
        <Card title="Verteilung nach Typ">
          {byTypeEntries.length === 0 ? (
            <p className="muted">Noch keine Module vorhanden.</p>
          ) : (
            <ul className="detailList">
              {byTypeEntries.map(([key, count]) => (
                <li key={key} className="detailRow">
                  <strong>{getLabel(moduleTypeOptions, key as ModuleType)}</strong>
                  <span>{count}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Verteilung nach Autonomie">
          {byAutonomyEntries.length === 0 ? (
            <p className="muted">Noch keine Module vorhanden.</p>
          ) : (
            <ul className="detailList">
              {byAutonomyEntries.map(([key, count]) => (
                <li key={key} className="detailRow">
                  <strong>{getLabel(moduleAutonomyLevelOptions, key as ModuleAutonomyLevel)}</strong>
                  <span>{count}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neues Modul' : `Modul bearbeiten #${editingId}`}>
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Module-ID (Slug)">
                <input className="input" value={form.module_id} onChange={(event) => setFormValue('module_id', event.target.value)} required />
              </FormField>

              <FormField label="Name">
                <input className="input" value={form.name} onChange={(event) => setFormValue('name', event.target.value)} required />
              </FormField>

              <FormField label="Typ">
                <select className="input" value={form.module_type} onChange={(event) => setFormValue('module_type', event.target.value as ModuleType)}>
                  {moduleTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Status">
                <select className="input" value={form.status} onChange={(event) => setFormValue('status', event.target.value as ModuleStatus)}>
                  {moduleStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Autonomie-Level">
                <select className="input" value={form.autonomy_level} onChange={(event) => setFormValue('autonomy_level', event.target.value as ModuleAutonomyLevel)}>
                  {moduleAutonomyLevelOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Zone">
                <input className="input" value={form.zone} onChange={(event) => setFormValue('zone', event.target.value)} />
              </FormField>

              <FormField label="Standort">
                <input className="input" value={form.location} onChange={(event) => setFormValue('location', event.target.value)} />
              </FormField>

              <FormField label="Reactor-ID (optional)">
                <input className="input" value={form.reactor_id} onChange={(event) => setFormValue('reactor_id', event.target.value)} />
              </FormField>

              <FormField label="Asset-ID (optional)">
                <input className="input" value={form.asset_id} onChange={(event) => setFormValue('asset_id', event.target.value)} />
              </FormField>

              <FormField label="DeviceNode-ID (optional)">
                <input className="input" value={form.device_node_id} onChange={(event) => setFormValue('device_node_id', event.target.value)} />
              </FormField>

              <FormField label="ROS Node Name">
                <input className="input" value={form.ros_node_name} onChange={(event) => setFormValue('ros_node_name', event.target.value)} />
              </FormField>

              <FormField label="MQTT Node ID">
                <input className="input" value={form.mqtt_node_id} onChange={(event) => setFormValue('mqtt_node_id', event.target.value)} />
              </FormField>

              <FormField label="Wiki-Referenz">
                <input className="input" value={form.wiki_ref} onChange={(event) => setFormValue('wiki_ref', event.target.value)} />
              </FormField>
            </div>

            <FormField label="Beschreibung">
              <textarea className="input textarea" rows={3} value={form.description} onChange={(event) => setFormValue('description', event.target.value)} />
            </FormField>

            <FormField label="Capabilities">
              <div className="chipList">
                {moduleCapabilityTypeOptions.map((option) => {
                  const active = form.capabilities.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      type="button"
                      className={`button buttonCompact ${active ? '' : 'buttonSecondary'}`}
                      onClick={() => toggleCapability(option.value)}
                    >
                      {active ? '✓ ' : ''}
                      {option.label}
                    </button>
                  );
                })}
              </div>
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Modul anlegen' : 'Modul speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Modul-Liste">
          <form className="entityForm" onSubmit={handleFilterSubmit}>
            <div className="formGrid">
              <FormField label="Typ">
                <select className="input" value={filters.module_type} onChange={(event) => setFilterValue('module_type', event.target.value)}>
                  <option value="">Alle</option>
                  {moduleTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Status">
                <select className="input" value={filters.status} onChange={(event) => setFilterValue('status', event.target.value)}>
                  <option value="">Alle</option>
                  {moduleStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Autonomie">
                <select className="input" value={filters.autonomy_level} onChange={(event) => setFilterValue('autonomy_level', event.target.value)}>
                  <option value="">Alle</option>
                  {moduleAutonomyLevelOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </FormField>

              <FormField label="Zone">
                <input className="input" value={filters.zone} onChange={(event) => setFilterValue('zone', event.target.value)} />
              </FormField>
            </div>

            <div className="buttonRow">
              <button className="button buttonSecondary" type="submit">Filter anwenden</button>
              <button className="button buttonSecondary" type="button" onClick={() => void resetFilters()}>Filter zuruecksetzen</button>
            </div>
          </form>

          {loading ? (
            <InlineMessage>Lade Module…</InlineMessage>
          ) : modules.length === 0 ? (
            <InlineMessage>Keine Module fuer den aktuellen Filter vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Typ</th>
                    <th>Status</th>
                    <th>Autonomie</th>
                    <th>Capabilities</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {modules.map((module) => (
                    <tr key={module.id}>
                      <td>
                        <button className="linkButton" type="button" onClick={() => void selectModule(module.id)}>
                          <div className="stackCompact">
                            <strong>{module.name}</strong>
                            <span className="muted">{module.module_id}</span>
                          </div>
                        </button>
                      </td>
                      <td>{getLabel(moduleTypeOptions, module.module_type)}</td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[module.id] ?? module.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [module.id]: event.target.value as ModuleStatus,
                              }))
                            }
                          >
                            {moduleStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === module.id}
                            onClick={() => void handleStatusUpdate(module)}
                          >
                            {statusSavingId === module.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>{getLabel(moduleAutonomyLevelOptions, module.autonomy_level)}</td>
                      <td>{module.capability_count}</td>
                      <td>
                        <div className="buttonRow">
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void selectModule(module.id)}>Details</button>
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(module.id)}>Bearbeiten</button>
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

      <div className="grid cols-2">
        <Card title={selected ? `Modul-Details #${selected.id}` : 'Modul-Details'}>
          {detailLoading ? <InlineMessage>Lade Modul…</InlineMessage> : null}
          {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}

          {!selected && !detailLoading ? (
            <InlineMessage>Waehle ein Modul aus der Liste, um Verknuepfungen und Capabilities zu sehen.</InlineMessage>
          ) : selected ? (
            <div className="detailList">
              <div className="detailRow"><strong>Module-ID</strong><span>{selected.module_id}</span></div>
              <div className="detailRow"><strong>Name</strong><span>{selected.name}</span></div>
              <div className="detailRow"><strong>Typ</strong><span>{getLabel(moduleTypeOptions, selected.module_type)}</span></div>
              <div className="detailRow"><strong>Status</strong><span className={badgeClass(selected.status)}>{getLabel(moduleStatusOptions, selected.status)}</span></div>
              <div className="detailRow"><strong>Autonomie</strong><span>{getLabel(moduleAutonomyLevelOptions, selected.autonomy_level)}</span></div>
              <div className="detailRow"><strong>Zone / Standort</strong><span>{[selected.zone, selected.location].filter(Boolean).join(' / ') || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>ROS Node</strong><span>{selected.ros_node_name || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>MQTT Node</strong><span>{selected.mqtt_node_id || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>Offene Incidents</strong><span>{selected.open_incident_count}</span></div>
              <div className="detailRow"><strong>Aktualisiert</strong><span>{formatDateTime(selected.updated_at)}</span></div>
              {selected.description ? <InlineMessage>{selected.description}</InlineMessage> : null}
            </div>
          ) : null}
        </Card>

        <Card title="Verknuepfungen & Capabilities">
          {!selected && !detailLoading ? (
            <InlineMessage>Kein Modul ausgewaehlt.</InlineMessage>
          ) : selected ? (
            <div className="stackBlock">
              <div>
                <h3>Capabilities</h3>
                {selected.capabilities.length === 0 ? (
                  <p className="muted">Keine Capabilities hinterlegt.</p>
                ) : (
                  <div className="chipList">
                    {selected.capabilities.map((capability) => (
                      <span key={capability.id} className={`badge badge-${capability.is_enabled ? 'active' : 'disabled'}`}>
                        {getLabel(moduleCapabilityTypeOptions, capability.capability_type)}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <h3>Reaktor</h3>
                {selected.reactor ? (
                  <div className="detailList">
                    <div className="detailRow"><strong>Name</strong><span><a className="linkButton" href={`/reactors`}>{selected.reactor.name}</a></span></div>
                    <div className="detailRow"><strong>Status</strong><span className={badgeClass(selected.reactor.status)}>{selected.reactor.status}</span></div>
                  </div>
                ) : (
                  <p className="muted">Kein Reaktor verknuepft.</p>
                )}
              </div>

              <div>
                <h3>DeviceNode</h3>
                {selected.device_node ? (
                  <div className="detailList">
                    <div className="detailRow"><strong>Name</strong><span>{selected.device_node.name}</span></div>
                    <div className="detailRow"><strong>Node-ID</strong><span>{selected.device_node.node_id || 'Nicht gesetzt'}</span></div>
                    <div className="detailRow"><strong>Typ</strong><span>{selected.device_node.node_type}</span></div>
                    <div className="detailRow"><strong>Status</strong><span className={badgeClass(selected.device_node.status)}>{selected.device_node.status}</span></div>
                  </div>
                ) : (
                  <p className="muted">Kein DeviceNode verknuepft.</p>
                )}
              </div>

              <div>
                <h3>Asset</h3>
                {selected.asset ? (
                  <div className="detailList">
                    <div className="detailRow"><strong>Name</strong><span><a className="linkButton" href={`/assets`}>{selected.asset.name}</a></span></div>
                    <div className="detailRow"><strong>Typ</strong><span>{selected.asset.asset_type}</span></div>
                    <div className="detailRow"><strong>Status</strong><span className={badgeClass(selected.asset.status)}>{selected.asset.status}</span></div>
                  </div>
                ) : (
                  <p className="muted">Kein Asset verknuepft.</p>
                )}
              </div>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
