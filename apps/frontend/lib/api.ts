const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type ApiErrorPayload = {
  detail?: string | Array<{ msg?: string }>;
};

function parseResponseBody(rawBody: string) {
  if (!rawBody) {
    return null;
  }

  try {
    return JSON.parse(rawBody);
  } catch {
    return rawBody;
  }
}

function getErrorMessage(payload: unknown, fallback: string) {
  if (!payload || typeof payload !== 'object') {
    return fallback;
  }

  const detail = (payload as ApiErrorPayload).detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const message = detail
      .map((entry) => entry.msg)
      .filter((entry): entry is string => Boolean(entry))
      .join('; ');

    if (message) {
      return message;
    }
  }

  return fallback;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers,
    cache: 'no-store',
  });

  const rawBody = await response.text();
  const payload = parseResponseBody(rawBody);

  if (!response.ok) {
    throw new Error(getErrorMessage(payload, `API request failed (${response.status})`));
  }

  return payload as T;
}
