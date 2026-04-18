'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Asset,
  InventoryItem,
  Label,
  LabelOverview,
  LabelTargetType,
  LabelType,
  labelTargetTypeOptions,
  labelTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type LabelFormState = {
  label_code: string;
  label_type: LabelType;
  target_type: LabelTargetType;
  target_id: string;
  display_name: string;
  location_snapshot: string;
  note: string;
  is_active: boolean;
};

type LabelFilters = {
  target_type: string;
  active: string;
};

function createEmptyLabelForm(): LabelFormState {
  return {
    label_code: '',
    label_type: 'qr',
    target_type: 'asset',
    target_id: '',
    display_name: '',
    location_snapshot: '',
    note: '',
    is_active: true,
  };
}

function createEmptyFilters(): LabelFilters {
  return {
    target_type: '',
    active: '',
  };
}

function toLabelFormState(label: Label): LabelFormState {
  return {
    label_code: label.label_code,
    label_type: label.label_type,
    target_type: label.target_type,
    target_id: String(label.target_id),
    display_name: label.display_name ?? '',
    location_snapshot: label.location_snapshot ?? '',
    note: label.note ?? '',
    is_active: label.is_active,
  };
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('de-DE');
}

function targetTypeLabel(value: LabelTargetType) {
  return labelTargetTypeOptions.find((option) => option.value === value)?.label ?? value;
}

export function LabelManager() {
  const [labels, setLabels] = useState<Label[]>([]);
  const [overview, setOverview] = useState<LabelOverview | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [selectedLabel, setSelectedLabel] = useState<Label | null>(null);
  const [filters, setFilters] = useState<LabelFilters>(createEmptyFilters);
  const [form, setForm] = useState<LabelFormState>(createEmptyLabelForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [toggleSavingId, setToggleSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  const selectableTargets = useMemo(() => {
    if (form.target_type === 'asset') {
      return assets.map((asset) => ({
        id: asset.id,
        label: `${asset.name} (${asset.location}${asset.zone ? ` / ${asset.zone}` : ''})`,
      }));
    }

    return inventoryItems.map((item) => ({
      id: item.id,
      label: `${item.name} (${item.location}${item.zone ? ` / ${item.zone}` : ''})`,
    }));
  }, [assets, form.target_type, inventoryItems]);

  async function fetchLabel(labelCode: string) {
    const label = await apiRequest<Label>(`/api/v1/labels/${encodeURIComponent(labelCode)}`);
    setSelectedLabel(label);
    return label;
  }

  async function loadData(nextFilters: LabelFilters = filters, preferredLabelCode?: string | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.target_type) params.set('target_type', nextFilters.target_type);
    if (nextFilters.active) params.set('active', nextFilters.active);
    const path = params.size > 0 ? `/api/v1/labels?${params.toString()}` : '/api/v1/labels';

    try {
      const [labelData, overviewData, assetData, inventoryData] = await Promise.all([
        apiRequest<Label[]>(path),
        apiRequest<LabelOverview>('/api/v1/labels/overview'),
        apiRequest<Asset[]>('/api/v1/assets'),
        apiRequest<InventoryItem[]>('/api/v1/inventory'),
      ]);
      setLabels(labelData);
      setOverview(overviewData);
      setAssets(assetData);
      setInventoryItems(inventoryData);

      if (labelData.length === 0) {
        setSelectedLabel(null);
        if (mode !== 'edit') {
          setForm(createEmptyLabelForm());
        }
        return;
      }

      const desiredLabelCode =
        preferredLabelCode && labelData.some((label) => label.label_code === preferredLabelCode)
          ? preferredLabelCode
          : selectedLabel && labelData.some((label) => label.id === selectedLabel.id)
            ? selectedLabel.label_code
            : labelData[0].label_code;

      await fetchLabel(desiredLabelCode);
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
    setForm(createEmptyLabelForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof LabelFormState>(key: Key, value: LabelFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function setFilterValue<Key extends keyof LabelFilters>(key: Key, value: LabelFilters[Key]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  async function startEdit(labelCode: string) {
    setFormError(null);
    try {
      const label = await fetchLabel(labelCode);
      setForm(toLabelFormState(label));
      setMode('edit');
      setEditingId(label.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  function buildPayload() {
    const targetId = Number.parseInt(form.target_id, 10);
    if (Number.isNaN(targetId)) {
      throw new Error('Zielobjekt muss ausgewaehlt werden.');
    }

    return {
      label_code: form.label_code || null,
      label_type: form.label_type,
      target_type: form.target_type,
      target_id: targetId,
      display_name: form.display_name || null,
      location_snapshot: form.location_snapshot || null,
      note: form.note || null,
      is_active: form.is_active,
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
        const created = await apiRequest<Label>('/api/v1/labels', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Label angelegt.');
        resetForm();
        await loadData(filters, created.label_code);
      } else if (editingId !== null) {
        const updated = await apiRequest<Label>(`/api/v1/labels/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Label aktualisiert.');
        resetForm();
        await loadData(filters, updated.label_code);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggleActive(label: Label) {
    setToggleSavingId(label.id);
    setPageError(null);
    setNotice(null);
    try {
      const updated = await apiRequest<Label>(`/api/v1/labels/${label.id}/active`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !label.is_active }),
      });
      setNotice(`Label ${updated.label_code} aktualisiert.`);
      await loadData(filters, updated.label_code);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setToggleSavingId(null);
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
        <h1>Labels / Traceability</h1>
        <p className="muted">
          QR- und Label-Referenzen fuer reale Assets und Materialien verwalten, damit Objekte im Lab schnell auffindbar bleiben.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Gelabelte Assets"><div className="kpi">{overview?.labeled_assets ?? 0}</div></Card>
        <Card title="Gelabeltes Inventory"><div className="kpi">{overview?.labeled_inventory_items ?? 0}</div></Card>
        <Card title="Letzte Labels"><div className="kpi">{overview?.recent_labels.length ?? 0}</div></Card>
      </div>

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neues Label' : `Label bearbeiten #${editingId}`}>
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Label-Code">
                <input
                  className="input"
                  value={form.label_code}
                  onChange={(event) => setFormValue('label_code', event.target.value)}
                  placeholder="leer = automatisch"
                />
              </FormField>

              <FormField label="Label-Typ">
                <select className="input" value={form.label_type} onChange={(event) => setFormValue('label_type', event.target.value as LabelType)}>
                  {labelTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Zieltyp">
                <select
                  className="input"
                  value={form.target_type}
                  onChange={(event) => {
                    setFormValue('target_type', event.target.value as LabelTargetType);
                    setFormValue('target_id', '');
                  }}
                >
                  {labelTargetTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Zielobjekt">
                <select className="input" value={form.target_id} onChange={(event) => setFormValue('target_id', event.target.value)} required>
                  <option value="">Auswaehlen</option>
                  {selectableTargets.map((target) => (
                    <option key={target.id} value={target.id}>
                      {target.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Display-Name">
                <input className="input" value={form.display_name} onChange={(event) => setFormValue('display_name', event.target.value)} />
              </FormField>

              <FormField label="Standort-Snapshot">
                <input className="input" value={form.location_snapshot} onChange={(event) => setFormValue('location_snapshot', event.target.value)} />
              </FormField>
            </div>

            <FormField label="Notiz">
              <textarea className="input textarea" rows={4} value={form.note} onChange={(event) => setFormValue('note', event.target.value)} />
            </FormField>

            <FormField label="Aktiv">
              <label className="buttonRow" style={{ minHeight: 44, alignItems: 'center' }}>
                <input type="checkbox" checked={form.is_active} onChange={(event) => setFormValue('is_active', event.target.checked)} />
                <span>Label ist aktiv</span>
              </label>
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert...' : mode === 'create' ? 'Label anlegen' : 'Label speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title={selectedLabel ? `Label-Detail: ${selectedLabel.label_code}` : 'Letzte Labels'}>
          {!selectedLabel ? (
            overview && overview.recent_labels.length > 0 ? (
              <div className="tableWrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Ziel</th>
                      <th>Aktiv</th>
                    </tr>
                  </thead>
                  <tbody>
                    {overview.recent_labels.map((label) => (
                      <tr key={label.id}>
                        <td>
                          <button className="linkButton" type="button" onClick={() => void fetchLabel(label.label_code)}>
                            {label.label_code}
                          </button>
                        </td>
                        <td>{label.target_name}</td>
                        <td>{label.is_active ? 'Ja' : 'Nein'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <InlineMessage>Noch keine Labels vorhanden.</InlineMessage>
            )
          ) : (
            <div className="stackBlock">
              <div className="buttonRow">
                <span className={`badge badge-${selectedLabel.is_active ? 'available' : 'archived'}`}>
                  {selectedLabel.is_active ? 'aktiv' : 'inaktiv'}
                </span>
                <span className="badge badge-info">{targetTypeLabel(selectedLabel.target_type)}</span>
              </div>

              <div className="detailList">
                <div className="detailRow"><span>Code</span><strong>{selectedLabel.label_code}</strong></div>
                <div className="detailRow"><span>Ziel</span><strong>{selectedLabel.target_name ?? 'Nicht aufloesbar'}</strong></div>
                <div className="detailRow"><span>Standort</span><strong>{selectedLabel.location_snapshot ?? selectedLabel.target_location ?? 'Nicht gesetzt'}</strong></div>
                <div className="detailRow"><span>Scan</span><strong>{selectedLabel.scan_path}</strong></div>
                <div className="detailRow"><span>Erstellt</span><strong>{formatDateTime(selectedLabel.created_at)}</strong></div>
              </div>

              <div className="qrPanel">
                <img className="qrPreview" src={`${apiBase}${selectedLabel.qr_path}`} alt={`QR ${selectedLabel.label_code}`} />
              </div>

              {selectedLabel.note ? <InlineMessage>{selectedLabel.note}</InlineMessage> : null}

              <div className="buttonRow">
                <a className="button buttonSecondary buttonCompact" href={selectedLabel.scan_path} target="_blank" rel="noreferrer">
                  Scan-Seite
                </a>
                <a className="button buttonSecondary buttonCompact" href={`${apiBase}${selectedLabel.qr_path}`} target="_blank" rel="noreferrer">
                  QR oeffnen
                </a>
                <a className="button buttonSecondary buttonCompact" href={selectedLabel.target_manager_path}>
                  Zielmodul
                </a>
                <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(selectedLabel.label_code)}>
                  Bearbeiten
                </button>
              </div>
            </div>
          )}
        </Card>
      </div>

      <Card title="Label-Liste">
        <form className="entityForm" onSubmit={handleFilterSubmit}>
          <div className="formGrid">
            <FormField label="Zieltyp">
              <select className="input" value={filters.target_type} onChange={(event) => setFilterValue('target_type', event.target.value)}>
                <option value="">Alle</option>
                {labelTargetTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField label="Aktiv">
              <select className="input" value={filters.active} onChange={(event) => setFilterValue('active', event.target.value)}>
                <option value="">Alle</option>
                <option value="true">Nur aktiv</option>
                <option value="false">Nur inaktiv</option>
              </select>
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
          <InlineMessage>Lade Labels...</InlineMessage>
        ) : labels.length === 0 ? (
          <InlineMessage>Keine Labels fuer den aktuellen Filter vorhanden.</InlineMessage>
        ) : (
          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Ziel</th>
                  <th>Standort</th>
                  <th>Aktiv</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {labels.map((label) => (
                  <tr key={label.id}>
                    <td>
                      <button className="linkButton" type="button" onClick={() => void fetchLabel(label.label_code)}>
                        <div className="stackCompact">
                          <strong>{label.label_code}</strong>
                          <span className="muted">{targetTypeLabel(label.target_type)}</span>
                        </div>
                      </button>
                    </td>
                    <td>{label.target_name ?? `#${label.target_id}`}</td>
                    <td>{label.location_snapshot ?? label.target_location ?? 'Nicht gesetzt'}</td>
                    <td>{label.is_active ? 'Ja' : 'Nein'}</td>
                    <td>
                      <div className="buttonRow">
                        <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void fetchLabel(label.label_code)}>
                          Details
                        </button>
                        <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(label.label_code)}>
                          Bearbeiten
                        </button>
                        <button
                          className="button buttonSecondary buttonCompact"
                          type="button"
                          disabled={toggleSavingId === label.id}
                          onClick={() => void handleToggleActive(label)}
                        >
                          {toggleSavingId === label.id ? '...' : label.is_active ? 'Deaktivieren' : 'Aktivieren'}
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
