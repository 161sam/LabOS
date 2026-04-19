'use client';

import { useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { Card } from './Card';
import { InlineMessage } from './InlineMessage';

type WikiPageSummary = {
  slug: string;
  title: string;
};

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

export function WikiBrowser() {
  const [pages, setPages] = useState<WikiPageSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    async function loadPages() {
      setLoading(true);
      setPageError(null);
      try {
        setPages(await apiRequest<WikiPageSummary[]>('/api/v1/wiki/pages'));
      } catch (error) {
        setPageError(getErrorMessage(error));
      } finally {
        setLoading(false);
      }
    }

    void loadPages();
  }, []);

  return (
    <Card title="Wiki">
      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {loading ? <InlineMessage>Lade Wiki-Seiten…</InlineMessage> : null}
      {!loading && pages.length === 0 ? <p className="muted">Noch keine Wiki-Seiten vorhanden.</p> : null}
      {pages.length > 0 ? (
        <ul>
          {pages.map((page) => (
            <li key={page.slug}>
              <strong>{page.title}</strong> - {page.slug}
            </li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
}
