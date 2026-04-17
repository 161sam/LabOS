'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { Reactor, ReactorStatus, reactorStatusOptions } from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type ReactorFormState = {
  name: string;
  reactor_type: string;
  status: ReactorStatus;
  volume_l: string;
  location: string;
  last_cleaned_at: string;
  notes: string;
};

function createEmptyReactorForm(): ReactorFormState {
  return {
    name: '',
    reactor_type: '',
    status: 'online',
    volume_l: '1.0',
    location: '',
    last_cleaned_at: '',
    notes: '',
  };
}

function toReactorFormState(reactor: Reactor): ReactorFormState {
  return {
    name: reactor.name,
    reactor_type: reactor.reactor_type,
    status: reactor.status,
    volume_l: String(reactor.volume_l),
    location: reactor.location ?? '',
    last_cleaned_at: reactor.last_cleaned_at ? reactor.last_cleaned_at.slice(0, 16) : '',
    notes: reactor.notes ?? '',
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
    return 'Nicht dokumentiert';
  }

  return new Date(value).toLocaleString('de-DE');
}

export function ReactorManager() {
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [form, setForm] = useState<ReactorFormState>(createEmptyReactorForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, ReactorStatus>>({});
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
      const reactorData = await apiRequest<Reactor[]>('/api/v1/reactors');
      setReactors(reactorData);
      setStatusDrafts(
        Object.fromEntries(reactorData.map((reactor) => [reactor.id, reactor.status])) as Record<number, ReactorStatus>,
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
    setForm(createEmptyReactorForm());
    setFormError(null);
  }

  async function startEdit(reactorId: number) {
    setDetailLoading(true);
    setFormError(null);
    setNotice(null);

    try {
      const reactor = await apiRequest<Reactor>(`/api/v1/reactors/${reactorId}`);
      setForm(toReactorFormState(reactor));
      setMode('edit');
      setEditingId(reactor.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  function setFormValue<Key extends keyof ReactorFormState>(key: Key, value: ReactorFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    const payload = {
      name: form.name,
      reactor_type: form.reactor_type,
      status: form.status,
      volume_l: Number(form.volume_l),
      location: form.location,
      last_cleaned_at: form.last_cleaned_at || null,
      notes: form.notes,
    };

    try {
      if (mode === 'create') {
        await apiRequest<Reactor>('/api/v1/reactors', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Reaktor angelegt.');
      } else if (editingId !== null) {
        await apiRequest<Reactor>(`/api/v1/reactors/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Reaktor aktualisiert.');
      }

      resetForm();
      await loadData();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(reactor: Reactor) {
    const nextStatus = statusDrafts[reactor.id] ?? reactor.status;
    if (nextStatus === reactor.status) {
      return;
    }

    setStatusSavingId(reactor.id);
    setPageError(null);
    setNotice(null);

    try {
      const updated = await apiRequest<Reactor>(`/api/v1/reactors/${reactor.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });

      setReactors((current) =>
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
        <h1>Reaktoren</h1>
        <p className="muted">Reaktoren verwalten, Stammdaten pflegen und Betriebsstatus ohne Seed-Abhängigkeit ändern.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neuer Reaktor' : `Reaktor bearbeiten #${editingId}`}>
          {detailLoading ? <InlineMessage>Lade Reaktor…</InlineMessage> : null}
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

              <FormField label="Typ">
                <input
                  className="input"
                  value={form.reactor_type}
                  onChange={(event) => setFormValue('reactor_type', event.target.value)}
                  required
                />
              </FormField>

              <FormField label="Status">
                <select
                  className="input"
                  value={form.status}
                  onChange={(event) => setFormValue('status', event.target.value as ReactorStatus)}
                >
                  {reactorStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
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

              <FormField label="Standort">
                <input
                  className="input"
                  value={form.location}
                  onChange={(event) => setFormValue('location', event.target.value)}
                />
              </FormField>

              <FormField label="Letzte Reinigung">
                <input
                  className="input"
                  type="datetime-local"
                  value={form.last_cleaned_at}
                  onChange={(event) => setFormValue('last_cleaned_at', event.target.value)}
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
                {submitting ? 'Speichert…' : mode === 'create' ? 'Reaktor anlegen' : 'Reaktor speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Bestehende Reaktoren">
          {loading ? (
            <InlineMessage>Lade Reaktoren…</InlineMessage>
          ) : reactors.length === 0 ? (
            <InlineMessage>Noch keine Reaktoren vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Typ</th>
                    <th>Status</th>
                    <th>Standort</th>
                    <th>Volumen</th>
                    <th>Reinigung</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {reactors.map((reactor) => (
                    <tr key={reactor.id}>
                      <td>{reactor.name}</td>
                      <td>{reactor.reactor_type}</td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[reactor.id] ?? reactor.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [reactor.id]: event.target.value as ReactorStatus,
                              }))
                            }
                          >
                            {reactorStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === reactor.id}
                            onClick={() => void handleStatusUpdate(reactor)}
                          >
                            {statusSavingId === reactor.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>{reactor.location || 'Nicht gesetzt'}</td>
                      <td>{reactor.volume_l} L</td>
                      <td>{formatDateTime(reactor.last_cleaned_at)}</td>
                      <td>
                        <button
                          className="button buttonSecondary buttonCompact"
                          type="button"
                          onClick={() => void startEdit(reactor.id)}
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
