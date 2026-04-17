'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Asset,
  Charge,
  Reactor,
  Task,
  TaskPriority,
  TaskStatus,
  taskPriorityOptions,
  taskStatusOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type TaskFormState = {
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_at: string;
  charge_id: string;
  reactor_id: string;
  asset_id: string;
};

type TaskFilters = {
  status: string;
  priority: string;
};

function createEmptyTaskForm(): TaskFormState {
  return {
    title: '',
    description: '',
    status: 'open',
    priority: 'normal',
    due_at: '',
    charge_id: '',
    reactor_id: '',
    asset_id: '',
  };
}

function toTaskFormState(task: Task): TaskFormState {
  return {
    title: task.title,
    description: task.description ?? '',
    status: task.status,
    priority: task.priority,
    due_at: task.due_at ? task.due_at.slice(0, 16) : '',
    charge_id: task.charge_id ? String(task.charge_id) : '',
    reactor_id: task.reactor_id ? String(task.reactor_id) : '',
    asset_id: task.asset_id ? String(task.asset_id) : '',
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

function formatAssignment(task: Task) {
  return [task.asset_name, task.reactor_name, task.charge_name].filter(Boolean).join(' / ') || 'Nicht zugeordnet';
}

export function TaskManager() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [charges, setCharges] = useState<Charge[]>([]);
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [filters, setFilters] = useState<TaskFilters>({ status: '', priority: '' });
  const [form, setForm] = useState<TaskFormState>(createEmptyTaskForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, TaskStatus>>({});
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusSavingId, setStatusSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadData(nextFilters: TaskFilters = filters) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.status) params.set('status', nextFilters.status);
    if (nextFilters.priority) params.set('priority', nextFilters.priority);
    const path = params.size > 0 ? `/api/v1/tasks?${params.toString()}` : '/api/v1/tasks';

    try {
      const [taskData, assetData, chargeData, reactorData] = await Promise.all([
        apiRequest<Task[]>(path),
        apiRequest<Asset[]>('/api/v1/assets'),
        apiRequest<Charge[]>('/api/v1/charges'),
        apiRequest<Reactor[]>('/api/v1/reactors'),
      ]);
      setTasks(taskData);
      setAssets(assetData);
      setCharges(chargeData);
      setReactors(reactorData);
      setStatusDrafts(
        Object.fromEntries(taskData.map((task) => [task.id, task.status])) as Record<number, TaskStatus>,
      );
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
    setForm(createEmptyTaskForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof TaskFormState>(key: Key, value: TaskFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function startEdit(taskId: number) {
    setDetailLoading(true);
    setFormError(null);
    setNotice(null);
    try {
      const task = await apiRequest<Task>(`/api/v1/tasks/${taskId}`);
      setForm(toTaskFormState(task));
      setMode('edit');
      setEditingId(task.id);
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
      title: form.title,
      description: form.description,
      status: form.status,
      priority: form.priority,
      due_at: form.due_at || null,
      charge_id: form.charge_id ? Number(form.charge_id) : null,
      reactor_id: form.reactor_id ? Number(form.reactor_id) : null,
      asset_id: form.asset_id ? Number(form.asset_id) : null,
    };

    try {
      if (mode === 'create') {
        await apiRequest<Task>('/api/v1/tasks', { method: 'POST', body: JSON.stringify(payload) });
        setNotice('Aufgabe angelegt.');
      } else if (editingId !== null) {
        await apiRequest<Task>(`/api/v1/tasks/${editingId}`, { method: 'PUT', body: JSON.stringify(payload) });
        setNotice('Aufgabe aktualisiert.');
      }
      resetForm();
      await loadData(filters);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(task: Task) {
    const nextStatus = statusDrafts[task.id] ?? task.status;
    if (nextStatus === task.status) {
      return;
    }

    setStatusSavingId(task.id);
    setPageError(null);
    setNotice(null);
    try {
      await apiRequest<Task>(`/api/v1/tasks/${task.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      setNotice(`Status von ${task.title} aktualisiert.`);
      await loadData(filters);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setStatusSavingId(null);
    }
  }

  async function applyFilters(nextFilters: TaskFilters) {
    setFilters(nextFilters);
    await loadData(nextFilters);
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Aufgaben</h1>
        <p className="muted">Operative Laborarbeit planen, zuordnen und entlang von Prioritaet und Status bearbeiten.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neue Aufgabe' : `Aufgabe bearbeiten #${editingId}`}>
          {detailLoading ? <InlineMessage>Lade Aufgabe…</InlineMessage> : null}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Titel">
                <input className="input" value={form.title} onChange={(event) => setFormValue('title', event.target.value)} required />
              </FormField>

              <FormField label="Prioritaet">
                <select className="input" value={form.priority} onChange={(event) => setFormValue('priority', event.target.value as TaskPriority)}>
                  {taskPriorityOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Status">
                <select className="input" value={form.status} onChange={(event) => setFormValue('status', event.target.value as TaskStatus)}>
                  {taskStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Faellig bis">
                <input className="input" type="datetime-local" value={form.due_at} onChange={(event) => setFormValue('due_at', event.target.value)} />
              </FormField>

              <FormField label="Charge">
                <select className="input" value={form.charge_id} onChange={(event) => setFormValue('charge_id', event.target.value)}>
                  <option value="">Nicht zugeordnet</option>
                  {charges.map((charge) => (
                    <option key={charge.id} value={charge.id}>
                      {charge.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Reaktor">
                <select className="input" value={form.reactor_id} onChange={(event) => setFormValue('reactor_id', event.target.value)}>
                  <option value="">Nicht zugeordnet</option>
                  {reactors.map((reactor) => (
                    <option key={reactor.id} value={reactor.id}>
                      {reactor.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Asset / Device">
                <select className="input" value={form.asset_id} onChange={(event) => setFormValue('asset_id', event.target.value)}>
                  <option value="">Nicht zugeordnet</option>
                  {assets.map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.name}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>

            <FormField label="Beschreibung">
              <textarea className="input textarea" rows={5} value={form.description} onChange={(event) => setFormValue('description', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Aufgabe anlegen' : 'Aufgabe speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Aufgabenliste">
          <div className="formGrid">
            <FormField label="Statusfilter">
              <select className="input" value={filters.status} onChange={(event) => void applyFilters({ ...filters, status: event.target.value })}>
                <option value="">Alle</option>
                {taskStatusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField label="Prioritaetsfilter">
              <select className="input" value={filters.priority} onChange={(event) => void applyFilters({ ...filters, priority: event.target.value })}>
                <option value="">Alle</option>
                {taskPriorityOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>
          </div>

          {loading ? (
            <InlineMessage>Lade Aufgaben…</InlineMessage>
          ) : tasks.length === 0 ? (
            <InlineMessage>Keine Aufgaben fuer den aktuellen Filter vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Titel</th>
                    <th>Prioritaet</th>
                    <th>Status</th>
                    <th>Faellig</th>
                    <th>Zuordnung</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((task) => (
                    <tr key={task.id}>
                      <td>
                        <div className="stackCompact">
                          <strong>{task.title}</strong>
                          <span className="muted">{task.description || 'Ohne Beschreibung'}</span>
                        </div>
                      </td>
                      <td><span className={badgeClass(task.priority)}>{task.priority}</span></td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[task.id] ?? task.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [task.id]: event.target.value as TaskStatus,
                              }))
                            }
                          >
                            {taskStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === task.id}
                            onClick={() => void handleStatusUpdate(task)}
                          >
                            {statusSavingId === task.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>{formatDateTime(task.due_at)}</td>
                      <td>{formatAssignment(task)}</td>
                      <td>
                        <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(task.id)}>
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
