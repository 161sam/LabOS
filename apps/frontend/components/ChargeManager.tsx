'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { Charge, ChargeStatus, Reactor, chargeStatusOptions } from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type ChargeFormState = {
  name: string;
  species: string;
  status: ChargeStatus;
  reactor_id: string;
  start_date: string;
  volume_l: string;
  notes: string;
};

function createEmptyChargeForm(): ChargeFormState {
  return {
    name: '',
    species: '',
    status: 'planned',
    reactor_id: '',
    start_date: new Date().toISOString().slice(0, 10),
    volume_l: '1.0',
    notes: '',
  };
}

function toChargeFormState(charge: Charge): ChargeFormState {
  return {
    name: charge.name,
    species: charge.species,
    status: charge.status,
    reactor_id: charge.reactor_id ? String(charge.reactor_id) : '',
    start_date: charge.start_date,
    volume_l: String(charge.volume_l),
    notes: charge.notes ?? '',
  };
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  return 'Unerwarteter Fehler';
}

export function ChargeManager() {
  const [charges, setCharges] = useState<Charge[]>([]);
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [form, setForm] = useState<ChargeFormState>(createEmptyChargeForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, ChargeStatus>>({});
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusSavingId, setStatusSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadData() {
    setLoading(true);
    setPageError(null);

    try {
      const [chargeData, reactorData] = await Promise.all([
        apiRequest<Charge[]>('/api/v1/charges'),
        apiRequest<Reactor[]>('/api/v1/reactors'),
      ]);

      setCharges(chargeData);
      setReactors(reactorData);
      setStatusDrafts(
        Object.fromEntries(chargeData.map((charge) => [charge.id, charge.status])) as Record<number, ChargeStatus>,
      );
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function resetForm() {
    setMode('create');
    setEditingId(null);
    setForm(createEmptyChargeForm());
    setFormError(null);
  }

  function getReactorName(reactorId: number | null) {
    if (reactorId === null) {
      return 'Nicht zugeordnet';
    }

    const reactor = reactors.find((entry) => entry.id === reactorId);
    return reactor ? reactor.name : `Reaktor #${reactorId}`;
  }

  async function startEdit(chargeId: number) {
    setDetailLoading(true);
    setFormError(null);
    setNotice(null);

    try {
      const charge = await apiRequest<Charge>(`/api/v1/charges/${chargeId}`);
      setForm(toChargeFormState(charge));
      setMode('edit');
      setEditingId(charge.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  function setFormValue<Key extends keyof ChargeFormState>(key: Key, value: ChargeFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    const payload = {
      name: form.name,
      species: form.species,
      status: form.status,
      reactor_id: form.reactor_id ? Number(form.reactor_id) : null,
      start_date: form.start_date,
      volume_l: Number(form.volume_l),
      notes: form.notes,
    };

    try {
      if (mode === 'create') {
        await apiRequest<Charge>('/api/v1/charges', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Charge angelegt.');
      } else if (editingId !== null) {
        await apiRequest<Charge>(`/api/v1/charges/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Charge aktualisiert.');
      }

      resetForm();
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(charge: Charge) {
    const nextStatus = statusDrafts[charge.id] ?? charge.status;
    if (nextStatus === charge.status) {
      return;
    }

    setStatusSavingId(charge.id);
    setPageError(null);
    setNotice(null);

    try {
      const updated = await apiRequest<Charge>(`/api/v1/charges/${charge.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });

      setCharges((current) =>
        current.map((entry) => (entry.id === updated.id ? updated : entry)),
      );
      setStatusDrafts((current) => ({ ...current, [updated.id]: updated.status }));
      setNotice(`Status von ${updated.name} aktualisiert.`);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setStatusSavingId(null);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Chargen</h1>
        <p className="muted">Chargen anlegen, bearbeiten und ihren Betriebsstatus direkt im System pflegen.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neue Charge' : `Charge bearbeiten #${editingId}`}>
          {detailLoading ? <InlineMessage>Lade Charge…</InlineMessage> : null}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Name">
                <input
                  className="input"
                  value={form.name}
                  onChange={(event) => setFormValue('name', event.target.value)}
                  required
                />
              </FormField>

              <FormField label="Spezies">
                <input
                  className="input"
                  value={form.species}
                  onChange={(event) => setFormValue('species', event.target.value)}
                  required
                />
              </FormField>

              <FormField label="Status">
                <select
                  className="input"
                  value={form.status}
                  onChange={(event) => setFormValue('status', event.target.value as ChargeStatus)}
                >
                  {chargeStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Reaktor">
                <select
                  className="input"
                  value={form.reactor_id}
                  onChange={(event) => setFormValue('reactor_id', event.target.value)}
                >
                  <option value="">Nicht zugeordnet</option>
                  {reactors.map((reactor) => (
                    <option key={reactor.id} value={reactor.id}>
                      {reactor.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Startdatum">
                <input
                  className="input"
                  type="date"
                  value={form.start_date}
                  onChange={(event) => setFormValue('start_date', event.target.value)}
                />
              </FormField>

              <FormField label="Volumen (L)">
                <input
                  className="input"
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={form.volume_l}
                  onChange={(event) => setFormValue('volume_l', event.target.value)}
                  required
                />
              </FormField>
            </div>

            <FormField label="Notizen">
              <textarea
                className="input textarea"
                rows={5}
                value={form.notes}
                onChange={(event) => setFormValue('notes', event.target.value)}
              />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Charge anlegen' : 'Charge speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Bestehende Chargen">
          {loading ? (
            <InlineMessage>Lade Chargen…</InlineMessage>
          ) : charges.length === 0 ? (
            <InlineMessage>Noch keine Chargen vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Spezies</th>
                    <th>Reaktor</th>
                    <th>Status</th>
                    <th>Start</th>
                    <th>Volumen</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {charges.map((charge) => (
                    <tr key={charge.id}>
                      <td>{charge.name}</td>
                      <td>{charge.species}</td>
                      <td>{getReactorName(charge.reactor_id)}</td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[charge.id] ?? charge.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [charge.id]: event.target.value as ChargeStatus,
                              }))
                            }
                          >
                            {chargeStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === charge.id}
                            onClick={() => void handleStatusUpdate(charge)}
                          >
                            {statusSavingId === charge.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>{charge.start_date}</td>
                      <td>{charge.volume_l} L</td>
                      <td>
                        <button
                          className="button buttonSecondary buttonCompact"
                          type="button"
                          onClick={() => void startEdit(charge.id)}
                        >
                          Bearbeiten
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
