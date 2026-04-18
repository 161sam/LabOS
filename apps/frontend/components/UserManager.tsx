'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { User, UserRole, userRoleOptions } from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type UserFormState = {
  username: string;
  display_name: string;
  email: string;
  password: string;
  role: UserRole;
  is_active: boolean;
  note: string;
};

function createEmptyUserForm(): UserFormState {
  return {
    username: '',
    display_name: '',
    email: '',
    password: '',
    role: 'viewer',
    is_active: true,
    note: '',
  };
}

function toUserFormState(user: User): UserFormState {
  return {
    username: user.username,
    display_name: user.display_name ?? '',
    email: user.email ?? '',
    password: '',
    role: user.role,
    is_active: user.is_active,
    note: user.note ?? '',
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
    return 'Nie';
  }
  return new Date(value).toLocaleString('de-DE');
}

function getRoleLabel(role: UserRole) {
  return userRoleOptions.find((option) => option.value === role)?.label ?? role;
}

export function UserManager() {
  const { user: currentUser, refreshAuth } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [form, setForm] = useState<UserFormState>(createEmptyUserForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);

  async function loadUsers(preferredUserId?: number | null) {
    setLoading(true);
    setPageError(null);
    try {
      const userData = await apiRequest<User[]>('/api/v1/users');
      setUsers(userData);
      const nextSelectedUser =
        preferredUserId && userData.some((item) => item.id === preferredUserId)
          ? userData.find((item) => item.id === preferredUserId) ?? null
          : selectedUser && userData.some((item) => item.id === selectedUser.id)
            ? userData.find((item) => item.id === selectedUser.id) ?? null
            : userData[0] ?? null;
      setSelectedUser(nextSelectedUser);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
  }, []);

  function setFormValue<Key extends keyof UserFormState>(key: Key, value: UserFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function resetForm() {
    setMode('create');
    setEditingId(null);
    setForm(createEmptyUserForm());
    setFormError(null);
  }

  function startEdit(user: User) {
    setSelectedUser(user);
    setMode('edit');
    setEditingId(user.id);
    setForm(toUserFormState(user));
    setFormError(null);
    setNotice(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    try {
      if (mode === 'create') {
        if (!form.password.trim()) {
          throw new Error('Passwort ist fuer neue Benutzer erforderlich');
        }

        const created = await apiRequest<User>('/api/v1/users', {
          method: 'POST',
          body: JSON.stringify({
            username: form.username,
            display_name: form.display_name || null,
            email: form.email || null,
            password: form.password,
            role: form.role,
            is_active: form.is_active,
            note: form.note || null,
          }),
        });
        setNotice(`Benutzer ${created.username} wurde angelegt.`);
        resetForm();
        await loadUsers(created.id);
        return;
      }

      if (!editingId) {
        throw new Error('Kein Benutzer zum Bearbeiten ausgewaehlt');
      }

      const updated = await apiRequest<User>(`/api/v1/users/${editingId}`, {
        method: 'PUT',
        body: JSON.stringify({
          username: form.username,
          display_name: form.display_name || null,
          email: form.email || null,
          role: form.role,
          is_active: form.is_active,
          note: form.note || null,
        }),
      });

      if (form.password.trim()) {
        await apiRequest<User>(`/api/v1/users/${editingId}/password`, {
          method: 'PATCH',
          body: JSON.stringify({ password: form.password }),
        });
      }

      if (currentUser && currentUser.id === editingId) {
        await refreshAuth();
      }

      setNotice(`Benutzer ${updated.username} wurde aktualisiert.`);
      setForm((current) => ({ ...current, password: '' }));
      await loadUsers(updated.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleUserActive(user: User) {
    setNotice(null);
    setFormError(null);
    try {
      const updated = await apiRequest<User>(`/api/v1/users/${user.id}/active`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !user.is_active }),
      });
      if (currentUser && currentUser.id === user.id) {
        await refreshAuth();
      }
      setNotice(`Benutzer ${updated.username} ist jetzt ${updated.is_active ? 'aktiv' : 'inaktiv'}.`);
      await loadUsers(updated.id);
      if (editingId === updated.id) {
        setForm(toUserFormState(updated));
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Benutzer und Rollen</h1>
        <p className="muted">Lokale Mehrnutzerbasis fuer Viewer, Operatoren und Admins. Nur Admins duerfen Benutzerkonten verwalten.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="Benutzerkonten">
          {loading ? (
            <InlineMessage>Lade Benutzer…</InlineMessage>
          ) : users.length === 0 ? (
            <p className="muted">Noch keine Benutzer vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Rolle</th>
                    <th>Status</th>
                    <th>Letzter Login</th>
                    <th>Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>
                        <button className="linkButton" type="button" onClick={() => startEdit(user)}>
                          <div className="stackCompact">
                            <strong>{user.display_name || user.username}</strong>
                            <span className="muted">{user.username}</span>
                          </div>
                        </button>
                      </td>
                      <td><span className={`badge badge-${user.role}`}>{getRoleLabel(user.role)}</span></td>
                      <td>
                        <span className={`badge badge-${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? 'aktiv' : 'inaktiv'}
                        </span>
                      </td>
                      <td>{formatDateTime(user.last_login_at)}</td>
                      <td>
                        <div className="buttonRow">
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => startEdit(user)}>
                            Bearbeiten
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void toggleUserActive(user)}>
                            {user.is_active ? 'Deaktivieren' : 'Aktivieren'}
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

        <Card title={mode === 'create' ? 'Neuen Benutzer anlegen' : `Benutzer ${selectedUser?.username ?? ''} bearbeiten`}>
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Username">
                <input
                  className="input"
                  value={form.username}
                  onChange={(event) => setFormValue('username', event.target.value)}
                  required
                />
              </FormField>

              <FormField label="Display Name">
                <input
                  className="input"
                  value={form.display_name}
                  onChange={(event) => setFormValue('display_name', event.target.value)}
                />
              </FormField>

              <FormField label="E-Mail">
                <input
                  className="input"
                  type="email"
                  value={form.email}
                  onChange={(event) => setFormValue('email', event.target.value)}
                />
              </FormField>

              <FormField label="Rolle">
                <select
                  className="input"
                  value={form.role}
                  onChange={(event) => setFormValue('role', event.target.value as UserRole)}
                >
                  {userRoleOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label={mode === 'create' ? 'Passwort' : 'Neues Passwort (optional)'}>
                <input
                  className="input"
                  type="password"
                  value={form.password}
                  onChange={(event) => setFormValue('password', event.target.value)}
                  required={mode === 'create'}
                />
              </FormField>

              <FormField label="Status">
                <label className="muted">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(event) => setFormValue('is_active', event.target.checked)}
                  />{' '}
                  Konto ist aktiv
                </label>
              </FormField>
            </div>

            <FormField label="Notiz">
              <textarea
                className="input textarea"
                value={form.note}
                onChange={(event) => setFormValue('note', event.target.value)}
              />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Benutzer anlegen' : 'Benutzer speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Zurueck zu Neu
                </button>
              ) : null}
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
