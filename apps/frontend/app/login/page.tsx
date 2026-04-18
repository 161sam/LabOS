'use client';

import { Suspense } from 'react';
import { FormEvent, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { useAuth } from '../../components/AuthProvider';
import { Card } from '../../components/Card';
import { FormField } from '../../components/FormField';
import { InlineMessage } from '../../components/InlineMessage';

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { status, login } = useAuth();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('labosadmin');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const nextPath = searchParams.get('next') || '/';

  useEffect(() => {
    if (status === 'authenticated') {
      router.replace(nextPath);
    }
  }, [nextPath, router, status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);

    try {
      await login(username, password);
      router.replace(nextPath);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="authCardWrap">
      <Card title="LabOS Login">
        <div className="stackBlock">
          <div className="stackCompact">
            <p>Lokale Anmeldung fuer den geschuetzten Mehrnutzerbetrieb von LabOS.</p>
            <p className="muted">Bootstrap fuer Dev lokal: `admin` / `labosadmin`. Diese Defaults muessen produktiv ersetzt werden.</p>
          </div>

          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <FormField label="Benutzername">
              <input
                className="input"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />
            </FormField>

            <FormField label="Passwort">
              <input
                className="input"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting || status === 'loading'}>
                {submitting ? 'Meldet an…' : 'Login'}
              </button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="authCardWrap">
          <Card title="LabOS Login">
            <p className="muted">Login-Ansicht wird geladen…</p>
          </Card>
        </div>
      }
    >
      <LoginPageContent />
    </Suspense>
  );
}
