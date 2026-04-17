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
      active_sensors: 0,
      error_sensors: 0,
      open_tasks: 0,
      due_today_tasks: 0,
      critical_alerts: 0,
      open_alerts: 0,
      sensor_overview: [],
      recent_alerts: [],
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
        <Card title="Offene Tasks"><div className="kpi">{data.open_tasks}</div></Card>
        <Card title="Heute faellig"><div className="kpi">{data.due_today_tasks}</div></Card>
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
          <p className="muted">Dashboard zeigt jetzt neben Sensorik auch offene Aufgaben und kritische Alerts fuer den Laboralltag.</p>
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title="Kritische Alerts">
          <div className="kpi">{data.critical_alerts}</div>
          <p className="muted">Unaufgeloeste Alerts mit hoher oder kritischer Relevanz bleiben damit operativ sichtbar.</p>
        </Card>

        <Card title="Letzte Alerts">
          {data.recent_alerts.length === 0 ? (
            <p className="muted">Noch keine Alerts vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Titel</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Erstellt</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_alerts.map((alert) => (
                    <tr key={alert.id}>
                      <td>{alert.title}</td>
                      <td><span className={`badge badge-${alert.severity}`}>{alert.severity}</span></td>
                      <td><span className={`badge badge-${alert.status}`}>{alert.status}</span></td>
                      <td>{new Date(alert.created_at).toLocaleString('de-DE')}</td>
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
