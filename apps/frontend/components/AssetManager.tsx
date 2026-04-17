'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Asset,
  AssetDetail,
  AssetOverview,
  AssetStatus,
  AssetType,
  assetStatusOptions,
  assetTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type AssetFormState = {
  name: string;
  asset_type: AssetType;
  category: string;
  status: AssetStatus;
  location: string;
  zone: string;
  serial_number: string;
  manufacturer: string;
  model: string;
  notes: string;
  maintenance_notes: string;
  last_maintenance_at: string;
  next_maintenance_at: string;
  wiki_ref: string;
};

type AssetFilters = {
  status: string;
  category: string;
  location: string;
  zone: string;
};

function createEmptyAssetForm(): AssetFormState {
  return {
    name: '',
    asset_type: 'lab_device',
    category: '',
    status: 'active',
    location: '',
    zone: '',
    serial_number: '',
    manufacturer: '',
    model: '',
    notes: '',
    maintenance_notes: '',
    last_maintenance_at: '',
    next_maintenance_at: '',
    wiki_ref: '',
  };
}

function createEmptyFilters(): AssetFilters {
  return {
    status: '',
    category: '',
    location: '',
    zone: '',
  };
}

function toAssetFormState(asset: Asset): AssetFormState {
  return {
    name: asset.name,
    asset_type: asset.asset_type,
    category: asset.category,
    status: asset.status,
    location: asset.location,
    zone: asset.zone ?? '',
    serial_number: asset.serial_number ?? '',
    manufacturer: asset.manufacturer ?? '',
    model: asset.model ?? '',
    notes: asset.notes ?? '',
    maintenance_notes: asset.maintenance_notes ?? '',
    last_maintenance_at: asset.last_maintenance_at ? asset.last_maintenance_at.slice(0, 16) : '',
    next_maintenance_at: asset.next_maintenance_at ? asset.next_maintenance_at.slice(0, 16) : '',
    wiki_ref: asset.wiki_ref ?? '',
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

function getAssetTypeLabel(assetType: AssetType) {
  return assetTypeOptions.find((option) => option.value === assetType)?.label ?? assetType;
}

function formatAssetPlacement(asset: { location: string; zone: string | null }) {
  const parts = [asset.location, asset.zone].filter(Boolean);
  return parts.join(' / ');
}

export function AssetManager() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [overview, setOverview] = useState<AssetOverview | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<AssetDetail | null>(null);
  const [filters, setFilters] = useState<AssetFilters>(createEmptyFilters);
  const [form, setForm] = useState<AssetFormState>(createEmptyAssetForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, AssetStatus>>({});
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

  async function fetchAssetDetail(assetId: number) {
    const detail = await apiRequest<AssetDetail>(`/api/v1/assets/${assetId}`);
    setSelectedAsset(detail);
    return detail;
  }

  async function loadData(nextFilters: AssetFilters = filters, preferredAssetId?: number | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.category) params.set('category', nextFilters.category);
    if (nextFilters.location) params.set('location', nextFilters.location);
    if (nextFilters.zone) params.set('zone', nextFilters.zone);
    const path = params.size > 0 ? `/api/v1/assets?${params.toString()}` : '/api/v1/assets';

    try {
      const [assetData, overviewData] = await Promise.all([
        apiRequest<Asset[]>(path),
        apiRequest<AssetOverview>('/api/v1/assets/overview'),
      ]);
      setAssets(assetData);
      setOverview(overviewData);
      setStatusDrafts(
        Object.fromEntries(assetData.map((asset) => [asset.id, asset.status])) as Record<number, AssetStatus>,
      );

      if (assetData.length === 0) {
        setSelectedAsset(null);
        if (mode !== 'edit') {
          setForm(createEmptyAssetForm());
        }
        return;
      }

      const desiredAssetId =
        preferredAssetId && assetData.some((asset) => asset.id === preferredAssetId)
          ? preferredAssetId
          : selectedAsset && assetData.some((asset) => asset.id === selectedAsset.id)
            ? selectedAsset.id
            : assetData[0].id;

      await fetchAssetDetail(desiredAssetId);
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
    setForm(createEmptyAssetForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof AssetFormState>(key: Key, value: AssetFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function setFilterValue<Key extends keyof AssetFilters>(key: Key, value: AssetFilters[Key]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  async function selectAsset(assetId: number) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      await fetchAssetDetail(assetId);
    } catch (error) {
      setDetailError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  async function startEdit(assetId: number) {
    setDetailLoading(true);
    setFormError(null);
    try {
      const detail = await fetchAssetDetail(assetId);
      setForm(toAssetFormState(detail));
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
      name: form.name,
      asset_type: form.asset_type,
      category: form.category,
      status: form.status,
      location: form.location,
      zone: form.zone || null,
      serial_number: form.serial_number || null,
      manufacturer: form.manufacturer || null,
      model: form.model || null,
      notes: form.notes || null,
      maintenance_notes: form.maintenance_notes || null,
      last_maintenance_at: form.last_maintenance_at || null,
      next_maintenance_at: form.next_maintenance_at || null,
      wiki_ref: form.wiki_ref || null,
    };

    try {
      if (mode === 'create') {
        const created = await apiRequest<Asset>('/api/v1/assets', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Asset angelegt.');
        resetForm();
        await loadData(filters, created.id);
      } else if (editingId !== null) {
        const updated = await apiRequest<Asset>(`/api/v1/assets/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Asset aktualisiert.');
        resetForm();
        await loadData(filters, updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(asset: Asset) {
    const nextStatus = statusDrafts[asset.id] ?? asset.status;
    if (nextStatus === asset.status) {
      return;
    }

    setStatusSavingId(asset.id);
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<Asset>(`/api/v1/assets/${asset.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      setNotice(`Status von ${asset.name} aktualisiert.`);
      await loadData(filters, asset.id);
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
    const emptyFilters = createEmptyFilters();
    setFilters(emptyFilters);
    await loadData(emptyFilters);
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Assets / Devices</h1>
        <p className="muted">
          Reale Geraete und operative Assets fuer BioOps, MakerOps, ITOps und Automation zentral pflegen.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-4">
        <Card title="Aktive Assets"><div className="kpi">{overview?.active_assets ?? 0}</div></Card>
        <Card title="In Wartung"><div className="kpi">{overview?.assets_in_maintenance ?? 0}</div></Card>
        <Card title="Fehlerstatus"><div className="kpi">{overview?.assets_in_error ?? 0}</div></Card>
        <Card title="Naechste Wartungen"><div className="kpi">{overview?.upcoming_maintenance_assets.length ?? 0}</div></Card>
      </div>

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neues Asset' : `Asset bearbeiten #${editingId}`}>
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Name">
                <input className="input" value={form.name} onChange={(event) => setFormValue('name', event.target.value)} required />
              </FormField>

              <FormField label="Typ">
                <select className="input" value={form.asset_type} onChange={(event) => setFormValue('asset_type', event.target.value as AssetType)}>
                  {assetTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Kategorie">
                <input className="input" value={form.category} onChange={(event) => setFormValue('category', event.target.value)} required />
              </FormField>

              <FormField label="Status">
                <select className="input" value={form.status} onChange={(event) => setFormValue('status', event.target.value as AssetStatus)}>
                  {assetStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Standort">
                <input className="input" value={form.location} onChange={(event) => setFormValue('location', event.target.value)} required />
              </FormField>

              <FormField label="Zone">
                <input className="input" value={form.zone} onChange={(event) => setFormValue('zone', event.target.value)} />
              </FormField>

              <FormField label="Seriennummer">
                <input className="input" value={form.serial_number} onChange={(event) => setFormValue('serial_number', event.target.value)} />
              </FormField>

              <FormField label="Hersteller">
                <input className="input" value={form.manufacturer} onChange={(event) => setFormValue('manufacturer', event.target.value)} />
              </FormField>

              <FormField label="Modell">
                <input className="input" value={form.model} onChange={(event) => setFormValue('model', event.target.value)} />
              </FormField>

              <FormField label="Wiki-Referenz">
                <input className="input" value={form.wiki_ref} onChange={(event) => setFormValue('wiki_ref', event.target.value)} />
              </FormField>

              <FormField label="Letzte Wartung">
                <input className="input" type="datetime-local" value={form.last_maintenance_at} onChange={(event) => setFormValue('last_maintenance_at', event.target.value)} />
              </FormField>

              <FormField label="Naechste Wartung">
                <input className="input" type="datetime-local" value={form.next_maintenance_at} onChange={(event) => setFormValue('next_maintenance_at', event.target.value)} />
              </FormField>
            </div>

            <FormField label="Allgemeine Notizen">
              <textarea className="input textarea" rows={4} value={form.notes} onChange={(event) => setFormValue('notes', event.target.value)} />
            </FormField>

            <FormField label="Wartungsnotizen">
              <textarea className="input textarea" rows={4} value={form.maintenance_notes} onChange={(event) => setFormValue('maintenance_notes', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Asset anlegen' : 'Asset speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Asset-Liste">
          <form className="entityForm" onSubmit={handleFilterSubmit}>
            <div className="formGrid">
              <FormField label="Statusfilter">
                <select className="input" value={filters.status} onChange={(event) => setFilterValue('status', event.target.value)}>
                  <option value="">Alle</option>
                  {assetStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Kategorie">
                <input className="input" value={filters.category} onChange={(event) => setFilterValue('category', event.target.value)} />
              </FormField>

              <FormField label="Standort">
                <input className="input" value={filters.location} onChange={(event) => setFilterValue('location', event.target.value)} />
              </FormField>

              <FormField label="Zone">
                <input className="input" value={filters.zone} onChange={(event) => setFilterValue('zone', event.target.value)} />
              </FormField>
            </div>

            <div className="buttonRow">
              <button className="button buttonSecondary" type="submit">Filter anwenden</button>
              <button className="button buttonSecondary" type="button" onClick={() => void resetFilters()}>
                Filter zuruecksetzen
              </button>
            </div>
          </form>

          {loading ? (
            <InlineMessage>Lade Assets…</InlineMessage>
          ) : assets.length === 0 ? (
            <InlineMessage>Keine Assets fuer den aktuellen Filter vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Typ</th>
                    <th>Status</th>
                    <th>Standort</th>
                    <th>Wartung</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.map((asset) => (
                    <tr key={asset.id}>
                      <td>
                        <button className="linkButton" type="button" onClick={() => void selectAsset(asset.id)}>
                          <div className="stackCompact">
                            <strong>{asset.name}</strong>
                            <span className="muted">{asset.category}</span>
                          </div>
                        </button>
                      </td>
                      <td>{getAssetTypeLabel(asset.asset_type)}</td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[asset.id] ?? asset.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [asset.id]: event.target.value as AssetStatus,
                              }))
                            }
                          >
                            {assetStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === asset.id}
                            onClick={() => void handleStatusUpdate(asset)}
                          >
                            {statusSavingId === asset.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>{formatAssetPlacement(asset)}</td>
                      <td>{formatDateTime(asset.next_maintenance_at)}</td>
                      <td>
                        <div className="buttonRow">
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void selectAsset(asset.id)}>
                            Details
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(asset.id)}>
                            Bearbeiten
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

      <div className="grid cols-2">
        <Card title={selectedAsset ? `Asset-Details #${selectedAsset.id}` : 'Asset-Details'}>
          {detailLoading ? <InlineMessage>Lade Asset…</InlineMessage> : null}
          {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}

          {!selectedAsset && !detailLoading ? (
            <InlineMessage>Waehle ein Asset aus der Liste, um Wartung, Tasks und Fotos zu sehen.</InlineMessage>
          ) : selectedAsset ? (
            <div className="detailList">
              <div className="detailRow"><strong>Name</strong><span>{selectedAsset.name}</span></div>
              <div className="detailRow"><strong>Typ</strong><span>{getAssetTypeLabel(selectedAsset.asset_type)}</span></div>
              <div className="detailRow"><strong>Status</strong><span className={badgeClass(selectedAsset.status)}>{selectedAsset.status}</span></div>
              <div className="detailRow"><strong>Kategorie</strong><span>{selectedAsset.category}</span></div>
              <div className="detailRow"><strong>Standort</strong><span>{selectedAsset.location}</span></div>
              <div className="detailRow"><strong>Zone</strong><span>{selectedAsset.zone || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>Seriennummer</strong><span>{selectedAsset.serial_number || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>Hersteller / Modell</strong><span>{[selectedAsset.manufacturer, selectedAsset.model].filter(Boolean).join(' / ') || 'Nicht gesetzt'}</span></div>
              <div className="detailRow"><strong>Letzte Wartung</strong><span>{formatDateTime(selectedAsset.last_maintenance_at)}</span></div>
              <div className="detailRow"><strong>Naechste Wartung</strong><span>{formatDateTime(selectedAsset.next_maintenance_at)}</span></div>
              <div className="detailRow"><strong>Offene Tasks</strong><span>{selectedAsset.open_task_count}</span></div>
              <div className="detailRow"><strong>Fotos</strong><span>{selectedAsset.photo_count}</span></div>
              <div className="detailRow"><strong>Wiki</strong><span>{selectedAsset.wiki_ref || 'Nicht gesetzt'}</span></div>
              {selectedAsset.notes ? <InlineMessage>{selectedAsset.notes}</InlineMessage> : null}
              {selectedAsset.maintenance_notes ? <InlineMessage>{selectedAsset.maintenance_notes}</InlineMessage> : null}
              {selectedAsset.wiki_ref ? (
                <div className="buttonRow">
                  <a className="button buttonSecondary buttonCompact" href="/wiki">
                    Wiki oeffnen
                  </a>
                </div>
              ) : null}
            </div>
          ) : null}
        </Card>

        <Card title="Verknuepfungen">
          {!selectedAsset && !detailLoading ? (
            <InlineMessage>Kein Asset ausgewaehlt.</InlineMessage>
          ) : selectedAsset ? (
            <div className="stackBlock">
              <div>
                <h3>Offene Tasks</h3>
                {selectedAsset.open_tasks.length === 0 ? (
                  <p className="muted">Keine offenen Tasks fuer dieses Asset.</p>
                ) : (
                  <div className="tableWrap">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Titel</th>
                          <th>Status</th>
                          <th>Prioritaet</th>
                          <th>Faellig</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedAsset.open_tasks.map((task) => (
                          <tr key={task.id}>
                            <td>{task.title}</td>
                            <td><span className={badgeClass(task.status)}>{task.status}</span></td>
                            <td><span className={badgeClass(task.priority)}>{task.priority}</span></td>
                            <td>{formatDateTime(task.due_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div>
                <h3>Letzte Fotos</h3>
                {selectedAsset.recent_photos.length === 0 ? (
                  <p className="muted">Noch keine Fotos zugeordnet.</p>
                ) : (
                  <div className="photoGrid">
                    {selectedAsset.recent_photos.map((photo) => (
                      <a
                        key={photo.id}
                        href={`${apiBase}${photo.file_url}`}
                        target="_blank"
                        rel="noreferrer"
                        className="photoTile"
                      >
                        <img className="photoThumb" src={`${apiBase}${photo.file_url}`} alt={photo.title || photo.original_filename} />
                        <div className="photoMeta">
                          <strong>{photo.title || photo.original_filename}</strong>
                          <span className="muted">{formatDateTime(photo.captured_at || photo.created_at)}</span>
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
