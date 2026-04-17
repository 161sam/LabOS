import { Card } from '../components/Card';
import { DashboardSummary } from '../lib/lab-resources';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

function formatSensorValue(value: number | null, unit: string) {
  if (value === null) {
    return 'Noch kein Wert';
  }

  return `${value} ${unit}`;
}

async function getSummary(): Promise<DashboardSummary> {
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
      active_sensors: 0,
      error_sensors: 0,
      sensor_overview: [],
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
        <Card title="Aktive Sensoren"><div className="kpi">{data.active_sensors}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Offene Alerts"><div className="kpi">{data.open_alerts}</div></Card>
        <Card title="Heutige Tasks"><div className="kpi">{data.today_tasks}</div></Card>
        <Card title="Sensorfehler"><div className="kpi">{data.error_sensors}</div></Card>
      </div>

      <div className="grid cols-2">
        <Card title="Letzte Sensorwerte">
          {data.sensor_overview.length === 0 ? (
            <p className="muted">Noch keine Sensordaten vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Sensor</th>
                    <th>Reaktor</th>
                    <th>Status</th>
                    <th>Letzter Wert</th>
                    <th>Zeitpunkt</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sensor_overview.map((sensor) => (
                    <tr key={sensor.id}>
                      <td>{sensor.name}</td>
                      <td>{sensor.reactor_name || sensor.location || 'Nicht zugeordnet'}</td>
                      <td>{sensor.status}</td>
                      <td>{formatSensorValue(sensor.last_value, sensor.unit)}</td>
                      <td>{sensor.last_recorded_at ? new Date(sensor.last_recorded_at).toLocaleString('de-DE') : 'Noch kein Wert'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Hinweis">
          <p>{data.message}</p>
          <p className="muted">Sensorik V1 liefert jetzt letzte Werte, Status und Verlauf als Grundlage fuer spaetere Alerts und Automatisierung.</p>
        </Card>
      </div>
    </div>
  );
}
