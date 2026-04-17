import { Card } from '../components/Card';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function getSummary() {
  try {
    const res = await fetch(`${apiBase}/api/v1/dashboard/summary`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Dashboard request failed');
    return res.json();
  } catch {
    return {
      active_charges: 0,
      reactors_online: 0,
      open_alerts: 0,
      today_tasks: 0,
      message: 'API noch nicht erreichbar – Frontend läuft trotzdem.'
    };
  }
}

export default async function DashboardPage() {
  const data = await getSummary();

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Dashboard</h1>
        <p className="muted">Zentrale Übersicht für Laborbetrieb, Chargen, Sensoren und Wiki.</p>
      </div>

      <div className="grid cols-3">
        <Card title="Aktive Chargen"><div className="kpi">{data.active_charges}</div></Card>
        <Card title="Reaktoren online"><div className="kpi">{data.reactors_online}</div></Card>
        <Card title="Offene Alerts"><div className="kpi">{data.open_alerts}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Heutige Tasks"><div className="kpi">{data.today_tasks}</div></Card>
        <Card title="Status"><span className="badge">Bootstrap V1</span></Card>
        <Card title="Hinweis"><p>{data.message}</p></Card>
      </div>
    </div>
  );
}
