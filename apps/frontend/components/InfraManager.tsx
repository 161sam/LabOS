'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  BackupRecord,
  InfraNode,
  InfraNodeDetail,
  InfraNodeRole,
  InfraNodeStatus,
  InfraNodeType,
  InfraOverview,
  InfraService,
  InfraServiceStatus,
  InfraServiceType,
  StorageVolume,
  infraNodeRoleOptions,
  infraNodeStatusOptions,
  infraNodeTypeOptions,
  infraServiceStatusOptions,
  infraServiceTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type NodeFormState = {
  node_id: string;
  name: string;
  node_type: InfraNodeType;
  status: InfraNodeStatus;
  role: InfraNodeRole;
  hostname: string;
  ip_address: string;
  zone: string;
  location: string;
  os_family: string;
  architecture: string;
  has_gpu: boolean;
  ros_enabled: boolean;
  mqtt_enabled: boolean;
  notes: string;
};

type NodeFilters = {
  node_type: string;
  status: string;
  role: string;
  zone: string;
};

type ServiceFormState = {
  service_name: string;
  service_type: InfraServiceType;
  status: InfraServiceStatus;
  endpoint: string;
  port: string;
  version: string;
};

function createEmptyNodeForm(): NodeFormState {
  return {
    node_id: '',
    name: '',
    node_type: 'server',
    status: 'nominal',
    role: 'general',
    hostname: '',
    ip_address: '',
    zone: '',
    location: '',
    os_family: '',
    architecture: '',
    has_gpu: false,
    ros_enabled: false,
    mqtt_enabled: false,
    notes: '',
  };
}

function createEmptyServiceForm(): ServiceFormState {
  return {
    service_name: '',
    service_type: 'api',
    status: 'nominal',
    endpoint: '',
    port: '',
    version: '',
  };
}

function createEmptyFilters(): NodeFilters {
  return { node_type: '', status: '', role: '', zone: '' };
}

function toNodeForm(detail: InfraNodeDetail): NodeFormState {
  return {
    node_id: detail.node_id,
    name: detail.name,
    node_type: detail.node_type,
    status: detail.status,
    role: detail.role,
    hostname: detail.hostname ?? '',
    ip_address: detail.ip_address ?? '',
    zone: detail.zone ?? '',
    location: detail.location ?? '',
    os_family: detail.os_family ?? '',
    architecture: detail.architecture ?? '',
    has_gpu: detail.has_gpu,
    ros_enabled: detail.ros_enabled,
    mqtt_enabled: detail.mqtt_enabled,
    notes: detail.notes ?? '',
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
    return '—';
  }
  return new Date(value).toLocaleString('de-DE');
}

function getLabel<T extends string>(
  options: ReadonlyArray<{ value: T; label: string }>,
  value: T,
): string {
  return options.find((option) => option.value === value)?.label ?? value;
}

function statusBadge(status: string) {
  const tone =
    status === 'nominal' || status === 'ok'
      ? 'success'
      : status === 'attention' || status === 'degraded' || status === 'warning'
        ? 'warning'
        : status === 'offline' || status === 'incident' || status === 'failed'
          ? 'danger'
          : 'muted';
  return <span className={`badge badge-${tone}`}>{status}</span>;
}

export function InfraManager() {
  const [nodes, setNodes] = useState<InfraNode[]>([]);
  const [overview, setOverview] = useState<InfraOverview | null>(null);
  const [selected, setSelected] = useState<InfraNodeDetail | null>(null);
  const [filters, setFilters] = useState<NodeFilters>(createEmptyFilters);
  const [nodeForm, setNodeForm] = useState<NodeFormState>(createEmptyNodeForm);
  const [serviceForm, setServiceForm] = useState<ServiceFormState>(createEmptyServiceForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, InfraNodeStatus>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [statusSavingId, setStatusSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [serviceError, setServiceError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  async function fetchDetail(nodeId: number) {
    const detail = await apiRequest<InfraNodeDetail>(`/api/v1/infra/nodes/${nodeId}`);
    setSelected(detail);
    return detail;
  }

  async function loadData(nextFilters: NodeFilters = filters, preferredId?: number | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.node_type) params.set('node_type', nextFilters.node_type);
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.role) params.set('role', nextFilters.role);
    if (nextFilters.zone) params.set('zone', nextFilters.zone);
    const path = params.size > 0 ? `/api/v1/infra/nodes?${params.toString()}` : '/api/v1/infra/nodes';

    try {
      const [list, overviewData] = await Promise.all([
        apiRequest<InfraNode[]>(path),
        apiRequest<InfraOverview>('/api/v1/infra/overview'),
      ]);
      setNodes(list);
      setOverview(overviewData);
      setStatusDrafts(
        Object.fromEntries(list.map((node) => [node.id, node.status])) as Record<
          number,
          InfraNodeStatus
        >,
      );

      if (list.length === 0) {
        setSelected(null);
        return;
      }

      const desiredId =
        preferredId && list.some((node) => node.id === preferredId)
          ? preferredId
          : selected && list.some((node) => node.id === selected.id)
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function resetNodeForm() {
    setMode('create');
    setEditingId(null);
    setNodeForm(createEmptyNodeForm());
    setFormError(null);
  }

  async function selectNode(nodeId: number) {
    setFormError(null);
    try {
      await fetchDetail(nodeId);
    } catch (error) {
      setPageError(getErrorMessage(error));
    }
  }

  async function startEdit(nodeId: number) {
    try {
      const detail = await fetchDetail(nodeId);
      setNodeForm(toNodeForm(detail));
      setMode('edit');
      setEditingId(detail.id);
      setFormError(null);
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  async function handleNodeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    const payload = {
      node_id: nodeForm.node_id,
      name: nodeForm.name,
      node_type: nodeForm.node_type,
      status: nodeForm.status,
      role: nodeForm.role,
      hostname: nodeForm.hostname || null,
      ip_address: nodeForm.ip_address || null,
      zone: nodeForm.zone || null,
      location: nodeForm.location || null,
      os_family: nodeForm.os_family || null,
      architecture: nodeForm.architecture || null,
      has_gpu: nodeForm.has_gpu,
      ros_enabled: nodeForm.ros_enabled,
      mqtt_enabled: nodeForm.mqtt_enabled,
      notes: nodeForm.notes || null,
    };

    try {
      if (mode === 'create') {
        const created = await apiRequest<InfraNodeDetail>('/api/v1/infra/nodes', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice(`Infra Node ${created.name} angelegt.`);
        resetNodeForm();
        await loadData(filters, created.id);
      } else if (editingId) {
        const updated = await apiRequest<InfraNodeDetail>(`/api/v1/infra/nodes/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice(`Infra Node ${updated.name} aktualisiert.`);
        resetNodeForm();
        await loadData(filters, updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(nodeId: number) {
    const nextStatus = statusDrafts[nodeId];
    if (!nextStatus) return;
    setStatusSavingId(nodeId);
    setNotice(null);
    try {
      await apiRequest(`/api/v1/infra/nodes/${nodeId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      await loadData(filters, nodeId);
      setNotice('Status aktualisiert.');
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

  async function handleServiceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setServiceError(null);
    const portParsed = serviceForm.port ? Number(serviceForm.port) : null;
    const payload = {
      infra_node_id: selected.id,
      service_name: serviceForm.service_name,
      service_type: serviceForm.service_type,
      status: serviceForm.status,
      endpoint: serviceForm.endpoint || null,
      port: portParsed,
      version: serviceForm.version || null,
    };
    try {
      await apiRequest<InfraService>('/api/v1/infra/services', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setServiceForm(createEmptyServiceForm());
      await loadData(filters, selected.id);
      setNotice('Service angelegt.');
    } catch (error) {
      setServiceError(getErrorMessage(error));
    }
  }

  return (
    <div className="stackBlock">
      <Card title="ITOps / InfraOps">
        <p className="muted">
          Operative Infrastruktur-Sicht: Hosts, SBCs, GPU-/Service-Nodes, Storage und Backup-Zustaende.
          Dies ist keine Monitoring-Plattform — Rohmetriken bleiben extern.
        </p>
        {pageError && <InlineMessage tone="error">{pageError}</InlineMessage>}
        {notice && <InlineMessage tone="success">{notice}</InlineMessage>}
      </Card>

      {overview && (
        <div className="grid cols-4">
          <Card title="Nodes gesamt"><div className="kpi">{overview.total_nodes}</div></Card>
          <Card title="Offline / Incident">
            <div className="kpi" style={{ color: overview.offline_nodes + overview.incident_nodes > 0 ? '#c53030' : undefined }}>
              {overview.offline_nodes + overview.incident_nodes}
            </div>
          </Card>
          <Card title="Degraded Services">
            <div className="kpi" style={{ color: overview.degraded_services > 0 ? '#dd6b20' : undefined }}>
              {overview.degraded_services}
            </div>
          </Card>
          <Card title="Backup-Fehler 14d">
            <div className="kpi" style={{ color: overview.recent_backup_failures > 0 ? '#c53030' : undefined }}>
              {overview.recent_backup_failures}
            </div>
          </Card>
        </div>
      )}

      {overview && (
        <div className="grid cols-2">
          <Card title="Nach Typ">
            <ul className="detailList">
              {Object.entries(overview.by_type).map(([type, count]) => (
                <li key={type} className="detailRow">
                  <span>{getLabel(infraNodeTypeOptions, type as InfraNodeType)}</span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </Card>
          <Card title="Nach Rolle">
            <ul className="detailList">
              {Object.entries(overview.by_role).map(([role, count]) => (
                <li key={role} className="detailRow">
                  <span>{getLabel(infraNodeRoleOptions, role as InfraNodeRole)}</span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      )}

      <Card title={mode === 'edit' ? 'Infra Node bearbeiten' : 'Neuen Infra Node anlegen'}>
        {formError && <InlineMessage tone="error">{formError}</InlineMessage>}
        <form onSubmit={handleNodeSubmit} className="entityForm">
          <div className="formGrid">
            <FormField label="Node ID (Slug)">
              <input
                className="input"
                value={nodeForm.node_id}
                onChange={(event) => setNodeForm({ ...nodeForm, node_id: event.target.value })}
                placeholder="server-1"
                required
              />
            </FormField>
            <FormField label="Name">
              <input
                className="input"
                value={nodeForm.name}
                onChange={(event) => setNodeForm({ ...nodeForm, name: event.target.value })}
                required
              />
            </FormField>
            <FormField label="Typ">
              <select
                className="input"
                value={nodeForm.node_type}
                onChange={(event) =>
                  setNodeForm({ ...nodeForm, node_type: event.target.value as InfraNodeType })
                }
              >
                {infraNodeTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Status">
              <select
                className="input"
                value={nodeForm.status}
                onChange={(event) =>
                  setNodeForm({ ...nodeForm, status: event.target.value as InfraNodeStatus })
                }
              >
                {infraNodeStatusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Rolle">
              <select
                className="input"
                value={nodeForm.role}
                onChange={(event) =>
                  setNodeForm({ ...nodeForm, role: event.target.value as InfraNodeRole })
                }
              >
                {infraNodeRoleOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Zone">
              <input
                className="input"
                value={nodeForm.zone}
                onChange={(event) => setNodeForm({ ...nodeForm, zone: event.target.value })}
              />
            </FormField>
            <FormField label="Hostname">
              <input
                className="input"
                value={nodeForm.hostname}
                onChange={(event) => setNodeForm({ ...nodeForm, hostname: event.target.value })}
              />
            </FormField>
            <FormField label="IP">
              <input
                className="input"
                value={nodeForm.ip_address}
                onChange={(event) => setNodeForm({ ...nodeForm, ip_address: event.target.value })}
              />
            </FormField>
            <FormField label="OS Family">
              <input
                className="input"
                value={nodeForm.os_family}
                onChange={(event) => setNodeForm({ ...nodeForm, os_family: event.target.value })}
              />
            </FormField>
            <FormField label="Architecture">
              <input
                className="input"
                value={nodeForm.architecture}
                onChange={(event) => setNodeForm({ ...nodeForm, architecture: event.target.value })}
              />
            </FormField>
          </div>
          <div className="buttonRow">
            <label className="stackCompact" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.4rem' }}>
              <input
                type="checkbox"
                checked={nodeForm.has_gpu}
                onChange={(event) => setNodeForm({ ...nodeForm, has_gpu: event.target.checked })}
              />
              <span>Hat GPU</span>
            </label>
            <label className="stackCompact" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.4rem' }}>
              <input
                type="checkbox"
                checked={nodeForm.ros_enabled}
                onChange={(event) => setNodeForm({ ...nodeForm, ros_enabled: event.target.checked })}
              />
              <span>ROS</span>
            </label>
            <label className="stackCompact" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.4rem' }}>
              <input
                type="checkbox"
                checked={nodeForm.mqtt_enabled}
                onChange={(event) =>
                  setNodeForm({ ...nodeForm, mqtt_enabled: event.target.checked })
                }
              />
              <span>MQTT</span>
            </label>
          </div>
          <FormField label="Notizen">
            <textarea
              className="input"
              value={nodeForm.notes}
              onChange={(event) => setNodeForm({ ...nodeForm, notes: event.target.value })}
              rows={2}
            />
          </FormField>
          <div className="buttonRow">
            <button className="button" type="submit" disabled={submitting}>
              {mode === 'edit' ? 'Aktualisieren' : 'Anlegen'}
            </button>
            {mode === 'edit' && (
              <button className="button buttonSecondary" type="button" onClick={resetNodeForm}>
                Abbrechen
              </button>
            )}
          </div>
        </form>
      </Card>

      <Card title="Filter">
        <form onSubmit={handleFilterSubmit} className="entityForm">
          <div className="formGrid">
          <FormField label="Typ">
            <select
              className="input"
              value={filters.node_type}
              onChange={(event) => setFilters({ ...filters, node_type: event.target.value })}
            >
              <option value="">Alle</option>
              {infraNodeTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Status">
            <select
              className="input"
              value={filters.status}
              onChange={(event) => setFilters({ ...filters, status: event.target.value })}
            >
              <option value="">Alle</option>
              {infraNodeStatusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Rolle">
            <select
              className="input"
              value={filters.role}
              onChange={(event) => setFilters({ ...filters, role: event.target.value })}
            >
              <option value="">Alle</option>
              {infraNodeRoleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Zone">
            <input
              className="input"
              value={filters.zone}
              onChange={(event) => setFilters({ ...filters, zone: event.target.value })}
            />
          </FormField>
          </div>
          <div className="buttonRow">
            <button className="button" type="submit" disabled={loading}>
              Anwenden
            </button>
            <button
              className="button buttonSecondary"
              type="button"
              onClick={() => {
                setFilters(createEmptyFilters());
                void loadData(createEmptyFilters());
              }}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>
      </Card>

      <Card title="Infra Nodes">
        {nodes.length === 0 ? (
          <p className="muted">Keine Nodes gefunden.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Rolle</th>
                <th>Status</th>
                <th>Zone</th>
                <th>Services</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((node) => (
                <tr key={node.id}>
                  <td>
                    <button className="linkButton" type="button" onClick={() => void selectNode(node.id)}>
                      {node.name}
                    </button>
                    <div className="muted">{node.node_id}</div>
                  </td>
                  <td>{getLabel(infraNodeTypeOptions, node.node_type)}</td>
                  <td>{getLabel(infraNodeRoleOptions, node.role)}</td>
                  <td>{statusBadge(node.status)}</td>
                  <td>{node.zone ?? '—'}</td>
                  <td>{node.service_count}</td>
                  <td>
                    <div className="buttonRow">
                      <select
                        className="input"
                        value={statusDrafts[node.id] ?? node.status}
                        onChange={(event) =>
                          setStatusDrafts((current) => ({
                            ...current,
                            [node.id]: event.target.value as InfraNodeStatus,
                          }))
                        }
                      >
                        {infraNodeStatusOptions.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <button
                        className="button buttonSecondary"
                        type="button"
                        onClick={() => void handleStatusUpdate(node.id)}
                        disabled={statusSavingId === node.id}
                      >
                        Setzen
                      </button>
                      <button
                        className="button buttonSecondary"
                        type="button"
                        onClick={() => void startEdit(node.id)}
                      >
                        Bearbeiten
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {selected && (
        <Card title={`Detail: ${selected.name}`}>
          <div className="grid cols-2">
            <div>
              <p><strong>Node ID:</strong> {selected.node_id}</p>
              <p><strong>Typ:</strong> {getLabel(infraNodeTypeOptions, selected.node_type)}</p>
              <p><strong>Rolle:</strong> {getLabel(infraNodeRoleOptions, selected.role)}</p>
              <p><strong>Status:</strong> {statusBadge(selected.status)}</p>
              <p><strong>Hostname:</strong> {selected.hostname ?? '—'}</p>
              <p><strong>IP:</strong> {selected.ip_address ?? '—'}</p>
              <p><strong>Zone:</strong> {selected.zone ?? '—'}</p>
            </div>
            <div>
              <p><strong>OS:</strong> {selected.os_family ?? '—'} / {selected.architecture ?? '—'}</p>
              <p><strong>GPU:</strong> {selected.has_gpu ? 'ja' : 'nein'}</p>
              <p><strong>ROS:</strong> {selected.ros_enabled ? 'ja' : 'nein'}</p>
              <p><strong>MQTT:</strong> {selected.mqtt_enabled ? 'ja' : 'nein'}</p>
              {selected.asset && (
                <p><strong>Asset:</strong> {selected.asset.name} ({selected.asset.asset_type})</p>
              )}
              {selected.autonomous_module && (
                <p><strong>Modul:</strong> {selected.autonomous_module.name} ({selected.autonomous_module.module_id})</p>
              )}
              {selected.notes && <p><strong>Notizen:</strong> {selected.notes}</p>}
            </div>
          </div>
        </Card>
      )}

      {selected && (
        <Card title="Services">
          {selected.services.length === 0 ? (
            <p className="muted">Keine Services zugeordnet.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Typ</th>
                  <th>Status</th>
                  <th>Endpoint</th>
                  <th>Port</th>
                  <th>Version</th>
                </tr>
              </thead>
              <tbody>
                {selected.services.map((service) => (
                  <tr key={service.id}>
                    <td>{service.service_name}</td>
                    <td>{getLabel(infraServiceTypeOptions, service.service_type)}</td>
                    <td>{statusBadge(service.status)}</td>
                    <td>{service.endpoint ?? '—'}</td>
                    <td>{service.port ?? '—'}</td>
                    <td>{service.version ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {serviceError && <InlineMessage tone="error">{serviceError}</InlineMessage>}
          <form onSubmit={handleServiceSubmit} className="stackCompact">
            <div className="grid cols-3">
              <FormField label="Service Name">
                <input
                  className="input"
                  value={serviceForm.service_name}
                  onChange={(event) =>
                    setServiceForm({ ...serviceForm, service_name: event.target.value })
                  }
                  required
                />
              </FormField>
              <FormField label="Typ">
                <select
                  className="input"
                  value={serviceForm.service_type}
                  onChange={(event) =>
                    setServiceForm({
                      ...serviceForm,
                      service_type: event.target.value as InfraServiceType,
                    })
                  }
                >
                  {infraServiceTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Status">
                <select
                  className="input"
                  value={serviceForm.status}
                  onChange={(event) =>
                    setServiceForm({
                      ...serviceForm,
                      status: event.target.value as InfraServiceStatus,
                    })
                  }
                >
                  {infraServiceStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Endpoint">
                <input
                  className="input"
                  value={serviceForm.endpoint}
                  onChange={(event) =>
                    setServiceForm({ ...serviceForm, endpoint: event.target.value })
                  }
                />
              </FormField>
              <FormField label="Port">
                <input
                  className="input"
                  value={serviceForm.port}
                  onChange={(event) => setServiceForm({ ...serviceForm, port: event.target.value })}
                />
              </FormField>
              <FormField label="Version">
                <input
                  className="input"
                  value={serviceForm.version}
                  onChange={(event) =>
                    setServiceForm({ ...serviceForm, version: event.target.value })
                  }
                />
              </FormField>
            </div>
            <div className="buttonRow">
              <button className="button buttonSecondary" type="submit">
                Service hinzufuegen
              </button>
            </div>
          </form>
        </Card>
      )}

      {selected && selected.storage_volumes.length > 0 && (
        <Card title="Storage">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Mount</th>
                <th>Typ</th>
                <th>Status</th>
                <th>Capacity (GB)</th>
                <th>Free (GB)</th>
              </tr>
            </thead>
            <tbody>
              {selected.storage_volumes.map((volume: StorageVolume) => (
                <tr key={volume.id}>
                  <td>{volume.name}</td>
                  <td>{volume.mount_path ?? '—'}</td>
                  <td>{volume.volume_type}</td>
                  <td>{statusBadge(volume.status)}</td>
                  <td>{volume.capacity_gb ?? '—'}</td>
                  <td>{volume.free_gb ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {selected && selected.recent_backups.length > 0 && (
        <Card title="Letzte Backups">
          <table className="table">
            <thead>
              <tr>
                <th>Typ</th>
                <th>Ziel</th>
                <th>Status</th>
                <th>Gestartet</th>
                <th>Beendet</th>
              </tr>
            </thead>
            <tbody>
              {selected.recent_backups.map((record: BackupRecord) => (
                <tr key={record.id}>
                  <td>{record.backup_type}</td>
                  <td>{record.target_id ?? '—'}</td>
                  <td>{statusBadge(record.status)}</td>
                  <td>{formatDateTime(record.started_at)}</td>
                  <td>{formatDateTime(record.finished_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
