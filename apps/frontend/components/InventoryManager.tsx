'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Asset,
  InventoryItem,
  InventoryOverview,
  InventoryStatus,
  Label,
  inventoryCategoryOptions,
  inventoryStatusOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type InventoryFormState = {
  name: string;
  category: string;
  status: InventoryStatus;
  quantity: string;
  unit: string;
  min_quantity: string;
  location: string;
  zone: string;
  supplier: string;
  sku: string;
  notes: string;
  asset_id: string;
  wiki_ref: string;
  last_restocked_at: string;
  expiry_date: string;
};

type InventoryFilters = {
  status: string;
  category: string;
  location: string;
  zone: string;
  search: string;
  low_stock: boolean;
};

function createEmptyInventoryForm(): InventoryFormState {
  return {
    name: '',
    category: '',
    status: 'available',
    quantity: '0',
    unit: '',
    min_quantity: '',
    location: '',
    zone: '',
    supplier: '',
    sku: '',
    notes: '',
    asset_id: '',
    wiki_ref: '',
    last_restocked_at: '',
    expiry_date: '',
  };
}

function createEmptyFilters(): InventoryFilters {
  return {
    status: '',
    category: '',
    location: '',
    zone: '',
    search: '',
    low_stock: false,
  };
}

function toInventoryFormState(item: InventoryItem): InventoryFormState {
  return {
    name: item.name,
    category: item.category,
    status: item.status,
    quantity: String(item.quantity),
    unit: item.unit,
    min_quantity: item.min_quantity === null ? '' : String(item.min_quantity),
    location: item.location,
    zone: item.zone ?? '',
    supplier: item.supplier ?? '',
    sku: item.sku ?? '',
    notes: item.notes ?? '',
    asset_id: item.asset_id === null ? '' : String(item.asset_id),
    wiki_ref: item.wiki_ref ?? '',
    last_restocked_at: item.last_restocked_at ? item.last_restocked_at.slice(0, 16) : '',
    expiry_date: item.expiry_date ?? '',
  };
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function formatDate(value: string | null) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleDateString('de-DE');
}

function formatDateTime(value: string | null) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

function formatQuantity(quantity: number, unit: string) {
  return `${quantity.toLocaleString('de-DE', { maximumFractionDigits: 3 })} ${unit}`;
}

function badgeClass(item: InventoryItem) {
  if (item.is_out_of_stock) {
    return 'badge badge-out_of_stock';
  }
  if (item.is_low_stock) {
    return 'badge badge-low_stock';
  }
  return `badge badge-${item.status}`;
}

function getCategoryLabel(category: string) {
  return inventoryCategoryOptions.find((option) => option.value === category)?.label ?? category;
}

export function InventoryManager() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [overview, setOverview] = useState<InventoryOverview | null>(null);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [selectedItemLabels, setSelectedItemLabels] = useState<Label[]>([]);
  const [filters, setFilters] = useState<InventoryFilters>(createEmptyFilters);
  const [form, setForm] = useState<InventoryFormState>(createEmptyInventoryForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, InventoryStatus>>({});
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

  async function fetchInventoryDetail(itemId: number) {
    const [detail, labels] = await Promise.all([
      apiRequest<InventoryItem>(`/api/v1/inventory/${itemId}`),
      apiRequest<Label[]>(`/api/v1/labels?target_type=inventory_item&target_id=${itemId}`),
    ]);
    setSelectedItem(detail);
    setSelectedItemLabels(labels);
    return detail;
  }

  async function loadData(nextFilters: InventoryFilters = filters, preferredItemId?: number | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.category) params.set('category', nextFilters.category);
    if (nextFilters.location) params.set('location', nextFilters.location);
    if (nextFilters.zone) params.set('zone', nextFilters.zone);
    if (nextFilters.search) params.set('search', nextFilters.search);
    if (nextFilters.low_stock) params.set('low_stock', 'true');
    const path = params.size > 0 ? `/api/v1/inventory?${params.toString()}` : '/api/v1/inventory';

    try {
      const [inventoryData, overviewData, assetData] = await Promise.all([
        apiRequest<InventoryItem[]>(path),
        apiRequest<InventoryOverview>('/api/v1/inventory/overview'),
        apiRequest<Asset[]>('/api/v1/assets'),
      ]);
      setItems(inventoryData);
      setOverview(overviewData);
      setAssets(assetData);
      setStatusDrafts(
        Object.fromEntries(inventoryData.map((item) => [item.id, item.status])) as Record<number, InventoryStatus>,
      );

      if (inventoryData.length === 0) {
        setSelectedItem(null);
        setSelectedItemLabels([]);
        if (mode !== 'edit') {
          setForm(createEmptyInventoryForm());
        }
        return;
      }

      const desiredItemId =
        preferredItemId && inventoryData.some((item) => item.id === preferredItemId)
          ? preferredItemId
          : selectedItem && inventoryData.some((item) => item.id === selectedItem.id)
            ? selectedItem.id
            : inventoryData[0].id;

      await fetchInventoryDetail(desiredItemId);
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
    setForm(createEmptyInventoryForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof InventoryFormState>(key: Key, value: InventoryFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function setFilterValue<Key extends keyof InventoryFilters>(key: Key, value: InventoryFilters[Key]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  async function selectItem(itemId: number) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      await fetchInventoryDetail(itemId);
    } catch (error) {
      setDetailError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  async function startEdit(itemId: number) {
    setDetailLoading(true);
    setFormError(null);
    try {
      const detail = await fetchInventoryDetail(itemId);
      setForm(toInventoryFormState(detail));
      setMode('edit');
      setEditingId(detail.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  function buildPayload() {
    const quantity = Number.parseFloat(form.quantity);
    const minQuantity = form.min_quantity ? Number.parseFloat(form.min_quantity) : null;

    if (Number.isNaN(quantity)) {
      throw new Error('Menge muss numerisch sein.');
    }
    if (minQuantity !== null && Number.isNaN(minQuantity)) {
      throw new Error('Mindestbestand muss numerisch sein.');
    }

    return {
      name: form.name,
      category: form.category,
      status: form.status,
      quantity,
      unit: form.unit,
      min_quantity: minQuantity,
      location: form.location,
      zone: form.zone || null,
      supplier: form.supplier || null,
      sku: form.sku || null,
      notes: form.notes || null,
      asset_id: form.asset_id ? Number.parseInt(form.asset_id, 10) : null,
      wiki_ref: form.wiki_ref || null,
      last_restocked_at: form.last_restocked_at || null,
      expiry_date: form.expiry_date || null,
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    try {
      const payload = buildPayload();
      if (mode === 'create') {
        const created = await apiRequest<InventoryItem>('/api/v1/inventory', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Material angelegt.');
        resetForm();
        await loadData(filters, created.id);
      } else if (editingId !== null) {
        const updated = await apiRequest<InventoryItem>(`/api/v1/inventory/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Material aktualisiert.');
        resetForm();
        await loadData(filters, updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(item: InventoryItem) {
    const nextStatus = statusDrafts[item.id] ?? item.status;
    if (nextStatus === item.status) {
      return;
    }

    setStatusSavingId(item.id);
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<InventoryItem>(`/api/v1/inventory/${item.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      setNotice(`Status von ${item.name} aktualisiert.`);
      await loadData(filters, item.id);
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
        <h1>Inventory / Materials</h1>
        <p className="muted">
          Materialien, Verbrauchsgueter und Lagerorte fuer BioOps, MakerOps, R&amp;D Ops und Automation pragmatisch pflegen.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-4">
        <Card title="Positionen"><div className="kpi">{overview?.total_items ?? 0}</div></Card>
        <Card title="Knapp"><div className="kpi">{overview?.low_stock_items ?? 0}</div></Card>
        <Card title="Leer"><div className="kpi">{overview?.out_of_stock_items ?? 0}</div></Card>
        <Card title="Kritisch"><div className="kpi">{overview?.critical_items.length ?? 0}</div></Card>
      </div>

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neues Material' : `Material bearbeiten #${editingId}`}>
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Name">
                <input className="input" value={form.name} onChange={(event) => setFormValue('name', event.target.value)} required />
              </FormField>

              <FormField label="Kategorie">
                <input
                  className="input"
                  list="inventory-category-options"
                  value={form.category}
                  onChange={(event) => setFormValue('category', event.target.value)}
                  required
                />
              </FormField>

              <FormField label="Status">
                <select className="input" value={form.status} onChange={(event) => setFormValue('status', event.target.value as InventoryStatus)}>
                  {inventoryStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Einheit">
                <input className="input" value={form.unit} onChange={(event) => setFormValue('unit', event.target.value)} required />
              </FormField>

              <FormField label="Menge">
                <input className="input" type="number" min="0" step="0.001" value={form.quantity} onChange={(event) => setFormValue('quantity', event.target.value)} required />
              </FormField>

              <FormField label="Mindestbestand">
                <input className="input" type="number" min="0" step="0.001" value={form.min_quantity} onChange={(event) => setFormValue('min_quantity', event.target.value)} />
              </FormField>

              <FormField label="Lagerort">
                <input className="input" value={form.location} onChange={(event) => setFormValue('location', event.target.value)} required />
              </FormField>

              <FormField label="Zone">
                <input className="input" value={form.zone} onChange={(event) => setFormValue('zone', event.target.value)} />
              </FormField>

              <FormField label="Lieferant">
                <input className="input" value={form.supplier} onChange={(event) => setFormValue('supplier', event.target.value)} />
              </FormField>

              <FormField label="SKU">
                <input className="input" value={form.sku} onChange={(event) => setFormValue('sku', event.target.value)} />
              </FormField>

              <FormField label="Asset-Zuordnung">
                <select className="input" value={form.asset_id} onChange={(event) => setFormValue('asset_id', event.target.value)}>
                  <option value="">Keine</option>
                  {assets.map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Wiki-Referenz">
                <input className="input" value={form.wiki_ref} onChange={(event) => setFormValue('wiki_ref', event.target.value)} />
              </FormField>

              <FormField label="Letztes Restock">
                <input className="input" type="datetime-local" value={form.last_restocked_at} onChange={(event) => setFormValue('last_restocked_at', event.target.value)} />
              </FormField>

              <FormField label="Ablaufdatum">
                <input className="input" type="date" value={form.expiry_date} onChange={(event) => setFormValue('expiry_date', event.target.value)} />
              </FormField>
            </div>

            <datalist id="inventory-category-options">
              {inventoryCategoryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </datalist>

            <FormField label="Notizen">
              <textarea className="input textarea" rows={4} value={form.notes} onChange={(event) => setFormValue('notes', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert...' : mode === 'create' ? 'Material anlegen' : 'Material speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title={selectedItem ? `Materialdetail: ${selectedItem.name}` : 'Kritische Materialien'}>
          {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}
          {detailLoading ? (
            <InlineMessage>Lade Materialdetail...</InlineMessage>
          ) : selectedItem ? (
            <div className="stackBlock">
              <div className="buttonRow">
                <span className={badgeClass(selectedItem)}>{selectedItem.status}</span>
                {selectedItem.needs_restock ? <span className="badge badge-critical">Restock noetig</span> : null}
              </div>

              <div className="detailList">
                <div className="detailRow"><span>Kategorie</span><strong>{getCategoryLabel(selectedItem.category)}</strong></div>
                <div className="detailRow"><span>Bestand</span><strong>{formatQuantity(selectedItem.quantity, selectedItem.unit)}</strong></div>
                <div className="detailRow"><span>Mindestbestand</span><strong>{selectedItem.min_quantity === null ? 'Nicht gesetzt' : formatQuantity(selectedItem.min_quantity, selectedItem.unit)}</strong></div>
                <div className="detailRow"><span>Ort</span><strong>{[selectedItem.location, selectedItem.zone].filter(Boolean).join(' / ') || 'Nicht gesetzt'}</strong></div>
                <div className="detailRow"><span>Asset</span><strong>{selectedItem.asset_name ?? 'Nicht zugeordnet'}</strong></div>
                <div className="detailRow"><span>Lieferant</span><strong>{selectedItem.supplier ?? 'Nicht gesetzt'}</strong></div>
                <div className="detailRow"><span>SKU</span><strong>{selectedItem.sku ?? 'Nicht gesetzt'}</strong></div>
                <div className="detailRow"><span>Letztes Restock</span><strong>{formatDateTime(selectedItem.last_restocked_at)}</strong></div>
                <div className="detailRow"><span>Ablaufdatum</span><strong>{formatDate(selectedItem.expiry_date)}</strong></div>
                <div className="detailRow"><span>Labels</span><strong>{selectedItemLabels.length}</strong></div>
                <div className="detailRow"><span>Wiki</span><strong>{selectedItem.wiki_ref ?? 'Nicht gesetzt'}</strong></div>
              </div>

              <div>
                <h3>Notizen</h3>
                <p className="muted">{selectedItem.notes ?? 'Keine Notizen hinterlegt.'}</p>
              </div>

              <div>
                <h3>Labels / QR</h3>
                {selectedItemLabels.length === 0 ? (
                  <p className="muted">Noch keine Labels fuer dieses Material vorhanden.</p>
                ) : (
                  <div className="tableWrap">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Code</th>
                          <th>Aktiv</th>
                          <th>Scan</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedItemLabels.map((label) => (
                          <tr key={label.id}>
                            <td>{label.label_code}</td>
                            <td>{label.is_active ? 'Ja' : 'Nein'}</td>
                            <td><a href={label.scan_path} target="_blank" rel="noreferrer">Oeffnen</a></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div className="buttonRow">
                <a className="button buttonSecondary" href="/labels">
                  In Traceability verwalten
                </a>
                <button className="button buttonSecondary" type="button" onClick={() => void startEdit(selectedItem.id)}>
                  Bearbeiten
                </button>
              </div>
            </div>
          ) : overview && overview.critical_items.length > 0 ? (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Bestand</th>
                    <th>Ort</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.critical_items.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <button className="linkButton" type="button" onClick={() => void selectItem(item.id)}>
                          {item.name}
                        </button>
                      </td>
                      <td><span className={badgeClass(item)}>{item.status}</span></td>
                      <td>{formatQuantity(item.quantity, item.unit)}</td>
                      <td>{item.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <InlineMessage>Keine kritischen Materialien vorhanden.</InlineMessage>
          )}
        </Card>
      </div>

      <Card title="Inventarliste">
        <form className="entityForm" onSubmit={handleFilterSubmit}>
          <div className="formGrid">
            <FormField label="Statusfilter">
              <select className="input" value={filters.status} onChange={(event) => setFilterValue('status', event.target.value)}>
                <option value="">Alle</option>
                {inventoryStatusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField label="Kategorie">
              <input className="input" value={filters.category} onChange={(event) => setFilterValue('category', event.target.value)} />
            </FormField>

            <FormField label="Lagerort">
              <input className="input" value={filters.location} onChange={(event) => setFilterValue('location', event.target.value)} />
            </FormField>

            <FormField label="Zone">
              <input className="input" value={filters.zone} onChange={(event) => setFilterValue('zone', event.target.value)} />
            </FormField>

            <FormField label="Suche">
              <input className="input" value={filters.search} onChange={(event) => setFilterValue('search', event.target.value)} placeholder="Name, SKU, Lieferant..." />
            </FormField>

            <FormField label="Kritisch">
              <label className="buttonRow" style={{ minHeight: 44, alignItems: 'center' }}>
                <input
                  type="checkbox"
                  checked={filters.low_stock}
                  onChange={(event) => setFilterValue('low_stock', event.target.checked)}
                />
                <span>Nur knappe / leere Positionen</span>
              </label>
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
          <InlineMessage>Lade Inventar...</InlineMessage>
        ) : items.length === 0 ? (
          <InlineMessage>Keine Materialien fuer den aktuellen Filter vorhanden.</InlineMessage>
        ) : (
          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Bestand</th>
                  <th>Ort</th>
                  <th>Asset</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <button className="linkButton" type="button" onClick={() => void selectItem(item.id)}>
                        <div className="stackCompact">
                          <strong>{item.name}</strong>
                          <span className="muted">{getCategoryLabel(item.category)}</span>
                        </div>
                      </button>
                    </td>
                    <td>
                      <div className="statusControl">
                        <select
                          className="input inputCompact"
                          value={statusDrafts[item.id] ?? item.status}
                          onChange={(event) =>
                            setStatusDrafts((current) => ({
                              ...current,
                              [item.id]: event.target.value as InventoryStatus,
                            }))
                          }
                        >
                          {inventoryStatusOptions.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                        <button
                          className="button buttonSecondary buttonCompact"
                          type="button"
                          disabled={statusSavingId === item.id}
                          onClick={() => void handleStatusUpdate(item)}
                        >
                          {statusSavingId === item.id ? '...' : 'Setzen'}
                        </button>
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <span className={badgeClass(item)}>{item.status}</span>
                      </div>
                    </td>
                    <td>
                      <div className="stackCompact">
                        <span>{formatQuantity(item.quantity, item.unit)}</span>
                        <span className="muted">
                          Min: {item.min_quantity === null ? 'nicht gesetzt' : formatQuantity(item.min_quantity, item.unit)}
                        </span>
                      </div>
                    </td>
                    <td>{[item.location, item.zone].filter(Boolean).join(' / ')}</td>
                    <td>{item.asset_name ?? '-'}</td>
                    <td>
                      <div className="buttonRow">
                        <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void selectItem(item.id)}>
                          Details
                        </button>
                        <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(item.id)}>
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
  );
}
