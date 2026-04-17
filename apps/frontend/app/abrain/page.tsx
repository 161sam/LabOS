const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function getAbrainStatus() {
  try {
    const res = await fetch(`${apiBase}/api/v1/abrain/status`, { cache: 'no-store' });
    if (!res.ok) throw new Error('failed');
    return res.json();
  } catch {
    return { connected: false, base_url: 'unbekannt', note: 'API nicht erreichbar' };
  }
}

export default async function ABrainPage() {
  const status = await getAbrainStatus();
  return (
    <div className="card">
      <h1>ABrain</h1>
      <p><strong>Verbunden:</strong> {String(status.connected)}</p>
      <p><strong>Base URL:</strong> {status.base_url}</p>
      <p><strong>Hinweis:</strong> {status.note}</p>
    </div>
  );
}
