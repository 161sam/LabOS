'use client';

import { useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { DashboardSummary } from '../lib/lab-resources';
import { Card } from './Card';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

function formatSensorValue(value: number | null, unit: string) {
  if (value === null) {
    return 'Noch kein Wert';
  }

  return `${value} ${unit}`;
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

export function DashboardClient() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSummary() {
      setLoading(true);
      setPageError(null);
      try {
        setData(await apiRequest<DashboardSummary>('/api/v1/dashboard/summary'));
      } catch (error) {
        setPageError(getErrorMessage(error));
      } finally {
        setLoading(false);
      }
    }

    void loadSummary();
  }, []);

  if (loading && !data) {
    return <InlineMessage>Lade Dashboard…</InlineMessage>;
  }

  if (!data) {
    return (
      <div className="grid" style={{ gap: 24 }}>
        <div>
          <h1>Dashboard</h1>
          <p className="muted">Zentrale Übersicht für Laborbetrieb, Chargen, Sensoren und Wiki.</p>
        </div>
        {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Dashboard</h1>
        <p className="muted">Zentrale Übersicht für Laborbetrieb, ReactorOps, Sensoren, Inventory, Labels und Mehrnutzerbetrieb.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}

      <div className="grid cols-3">
        <Card title="Aktive Chargen"><div className="kpi">{data.active_charges}</div></Card>
        <Card title="Reaktoren online"><div className="kpi">{data.reactors_online}</div></Card>
        <Card title="Aktive Sensoren"><div className="kpi">{data.active_sensors}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="ReactorOps Attention"><div className="kpi">{data.reactors_attention}</div></Card>
        <Card title="Harvest Ready"><div className="kpi">{data.reactors_harvest_ready}</div></Card>
        <Card title="Incident / Contamination"><div className="kpi">{data.reactors_incident_or_contamination}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Offline Devices"><div className="kpi">{data.offline_devices}</div></Card>
        <Card title="Reactor Control Layer"><div className="kpi">{data.reactor_telemetry_overview.length}</div></Card>
        <Card title="Offene Alerts"><div className="kpi">{data.open_alerts}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Safety Incidents (offen)"><div className="kpi" style={{ color: data.open_safety_incidents > 0 ? '#e53e3e' : undefined }}>{data.open_safety_incidents}</div></Card>
        <Card title="Kalibrierung fällig/abgelaufen"><div className="kpi" style={{ color: data.calibration_due_or_expired > 0 ? '#dd6b20' : undefined }}>{data.calibration_due_or_expired}</div></Card>
        <Card title="Wartung überfällig"><div className="kpi" style={{ color: data.maintenance_overdue > 0 ? '#dd6b20' : undefined }}>{data.maintenance_overdue}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Aktive Assets"><div className="kpi">{data.active_assets}</div></Card>
        <Card title="Assets in Wartung"><div className="kpi">{data.assets_in_maintenance}</div></Card>
        <Card title="Assets im Fehler"><div className="kpi">{data.assets_in_error}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Inventory Positionen"><div className="kpi">{data.inventory_items}</div></Card>
        <Card title="Inventory knapp"><div className="kpi">{data.inventory_low_stock}</div></Card>
        <Card title="Inventory leer"><div className="kpi">{data.inventory_out_of_stock}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Gelabelte Assets"><div className="kpi">{data.labeled_assets}</div></Card>
        <Card title="Gelabeltes Inventory"><div className="kpi">{data.labeled_inventory_items}</div></Card>
        <Card title="Letzte Labels"><div className="kpi">{data.recent_labels.length}</div></Card>
      </div>

      <div className="grid cols-3">
        <Card title="Offene Tasks"><div className="kpi">{data.open_tasks}</div></Card>
        <Card title="Heute faellig"><div className="kpi">{data.due_today_tasks}</div></Card>
        <Card title="Aktive Regeln"><div className="kpi">{data.active_rules}</div></Card>
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
          <p className="muted">Dashboard zeigt jetzt neben Labor-KPIs auch ReactorOps-Zustaende, Reactor-Control-Telemetrie, Device-Status und den geschuetzten Mehrnutzerbetrieb mit Rollenbasis an.</p>
          <div className="buttonRow">
            <a className="button buttonSecondary" href="/reactor-ops">
              Zu ReactorOps
            </a>
            <a className="button buttonSecondary" href="/reactor-control">
              Zu ReactorControl
            </a>
            <a className="button buttonSecondary" href="/abrain">
              Zu ABrain
            </a>
            <a className="button buttonSecondary" href="/assets">
              Zu AssetOps
            </a>
            <a className="button buttonSecondary" href="/inventory">
              Zu Inventory
            </a>
            <a className="button buttonSecondary" href="/labels">
              Zu Labels
            </a>
          </div>
        </Card>
      </div>

      <div className="grid cols-3">
        <Card title="Sensorfehler">
          <div className="kpi">{data.error_sensors}</div>
        </Card>

        <Card title="Kritische Alerts">
          <div className="kpi">{data.critical_alerts}</div>
          <p className="muted">Unaufgeloeste Alerts mit hoher oder kritischer Relevanz bleiben operativ sichtbar.</p>
        </Card>

        <Card title="Uploads 7 Tage">
          <div className="kpi">{data.uploads_last_7_days}</div>
          <p className="muted">Neue Bilddokumentation der letzten sieben Tage fuer Verlauf und Nachweis.</p>
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title="Naechste Wartungen">
          {data.upcoming_maintenance_assets.length === 0 ? (
            <p className="muted">Keine Wartungstermine hinterlegt.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Asset</th>
                    <th>Status</th>
                    <th>Standort</th>
                    <th>Termin</th>
                  </tr>
                </thead>
                <tbody>
                  {data.upcoming_maintenance_assets.map((asset) => (
                    <tr key={asset.id}>
                      <td>{asset.name}</td>
                      <td><span className={`badge badge-${asset.status}`}>{asset.status}</span></td>
                      <td>{asset.location}</td>
                      <td>{asset.next_maintenance_at ? new Date(asset.next_maintenance_at).toLocaleString('de-DE') : 'Nicht gesetzt'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Letzte Regelereignisse">
          {data.recent_rule_executions.length === 0 ? (
            <p className="muted">Noch keine Regelevaluierungen vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Regel</th>
                    <th>Status</th>
                    <th>Dry-Run</th>
                    <th>Zeitpunkt</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_rule_executions.map((execution) => (
                    <tr key={execution.id}>
                      <td>{execution.rule_name || `Rule #${execution.rule_id}`}</td>
                      <td><span className={`badge badge-${execution.status}`}>{execution.status}</span></td>
                      <td>{execution.dry_run ? 'Ja' : 'Nein'}</td>
                      <td>{new Date(execution.created_at).toLocaleString('de-DE')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Reactor Telemetry">
          {data.reactor_telemetry_overview.length === 0 ? (
            <p className="muted">Noch keine Reactor-Control-Telemetry vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Reaktor</th>
                    <th>Temp</th>
                    <th>pH</th>
                    <th>Last Telemetry</th>
                  </tr>
                </thead>
                <tbody>
                  {data.reactor_telemetry_overview.map((item) => (
                    <tr key={item.reactor_id}>
                      <td>{item.reactor_name}</td>
                      <td>{item.latest_temp !== null ? `${item.latest_temp} ${item.latest_temp_unit || ''}` : 'n/a'}</td>
                      <td>{item.latest_ph !== null ? `${item.latest_ph} ${item.latest_ph_unit || ''}` : 'n/a'}</td>
                      <td>{item.last_telemetry_at ? new Date(item.last_telemetry_at).toLocaleString('de-DE') : 'Noch kein Wert'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Letzte Reactor Events">
          {data.recent_reactor_events.length === 0 ? (
            <p className="muted">Noch keine ReactorOps-Ereignisse vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Reaktor</th>
                    <th>Typ</th>
                    <th>Titel</th>
                    <th>Zeitpunkt</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_reactor_events.map((event) => (
                    <tr key={event.id}>
                      <td>{event.reactor_name || `Reaktor #${event.reactor_id}`}</td>
                      <td><span className={`badge badge-${event.severity || 'info'}`}>{event.event_type}</span></td>
                      <td>{event.title}</td>
                      <td>{new Date(event.created_at).toLocaleString('de-DE')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Kritische Materialien">
          {data.critical_inventory_items.length === 0 ? (
            <p className="muted">Keine kritischen Materialien vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Material</th>
                    <th>Status</th>
                    <th>Bestand</th>
                    <th>Ort</th>
                  </tr>
                </thead>
                <tbody>
                  {data.critical_inventory_items.map((item) => (
                    <tr key={item.id}>
                      <td>{item.name}</td>
                      <td><span className={`badge badge-${item.status}`}>{item.status}</span></td>
                      <td>{item.quantity} {item.unit}</td>
                      <td>{item.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Letzte Labels">
          {data.recent_labels.length === 0 ? (
            <p className="muted">Noch keine Labels vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Ziel</th>
                    <th>Typ</th>
                    <th>Aktiv</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_labels.map((label) => (
                    <tr key={label.id}>
                      <td><a href={label.scan_path}>{label.label_code}</a></td>
                      <td>{label.target_name ?? `#${label.target_id}`}</td>
                      <td>{label.target_type}</td>
                      <td>{label.is_active ? 'Ja' : 'Nein'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
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

        <Card title="Letzte Uploads">
          {data.recent_photos.length === 0 ? (
            <p className="muted">Noch keine Fotos vorhanden.</p>
          ) : (
            <div className="photoGrid">
              {data.recent_photos.map((photo) => (
                <a
                  key={photo.id}
                  href={`${apiBase}${photo.file_url}`}
                  target="_blank"
                  rel="noreferrer"
                  className="photoTile"
                >
                  <img
                    className="photoThumb"
                    src={`${apiBase}${photo.file_url}`}
                    alt={photo.title || photo.original_filename}
                  />
                  <div className="photoMeta">
                    <strong>{photo.title || photo.original_filename}</strong>
                    <span className="muted">
                      {photo.asset_name || photo.charge_name || photo.reactor_name || 'Nicht zugeordnet'}
                    </span>
                  </div>
                </a>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
