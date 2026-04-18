'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  DeviceNode,
  deviceNodeTypeOptions,
  MQTTBridgeStatus,
  ReactorCommand,
  ReactorCommandType,
  reactorCommandTypeOptions,
  ReactorControlParameter,
  reactorControlParameterOptions,
  ReactorSetpoint,
  ReactorSetpointMode,
  reactorSetpointModeOptions,
  ReactorTwin,
  TelemetryValue,
  telemetrySensorTypeOptions,
} from '../lib/lab-resources';
import { useAuth } from './AuthProvider';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type CreateSetpointFormState = {
  parameter: ReactorControlParameter;
  target_value: string;
  min_value: string;
  max_value: string;
  mode: ReactorSetpointMode;
};

type EditSetpointFormState = {
  target_value: string;
  min_value: string;
  max_value: string;
  mode: ReactorSetpointMode;
};

function createSetpointFormState(): CreateSetpointFormState {
  return {
    parameter: 'temp',
    target_value: '',
    min_value: '',
    max_value: '',
    mode: 'manual',
  };
}

function toEditSetpointFormState(setpoint: ReactorSetpoint): EditSetpointFormState {
  return {
    target_value: String(setpoint.target_value),
    min_value: setpoint.min_value === null ? '' : String(setpoint.min_value),
    max_value: setpoint.max_value === null ? '' : String(setpoint.max_value),
    mode: setpoint.mode,
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
    return 'Nicht dokumentiert';
  }
  return new Date(value).toLocaleString('de-DE');
}

function getOptionLabel<T extends string>(options: ReadonlyArray<{ value: T; label: string }>, value: T) {
  return options.find((option) => option.value === value)?.label ?? value;
}

function toNumberOrNull(value: string) {
  if (!value.trim()) {
    return null;
  }
  return Number(value);
}

export function ReactorControlManager() {
  const { user } = useAuth();
  const canEdit = user?.role === 'admin' || user?.role === 'operator';
  const [reactors, setReactors] = useState<ReactorTwin[]>([]);
  const [selectedReactorId, setSelectedReactorId] = useState<number | null>(null);
  const [latestTelemetry, setLatestTelemetry] = useState<TelemetryValue[]>([]);
  const [telemetryHistory, setTelemetryHistory] = useState<TelemetryValue[]>([]);
  const [devices, setDevices] = useState<DeviceNode[]>([]);
  const [mqttStatus, setMqttStatus] = useState<MQTTBridgeStatus | null>(null);
  const [setpoints, setSetpoints] = useState<ReactorSetpoint[]>([]);
  const [commands, setCommands] = useState<ReactorCommand[]>([]);
  const [createSetpointForm, setCreateSetpointForm] = useState<CreateSetpointFormState>(createSetpointFormState);
  const [editSetpointForms, setEditSetpointForms] = useState<Record<number, EditSetpointFormState>>({});
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [setpointError, setSetpointError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [savingSetpointId, setSavingSetpointId] = useState<number | null>(null);
  const [creatingSetpoint, setCreatingSetpoint] = useState(false);
  const [sendingCommand, setSendingCommand] = useState<ReactorCommandType | null>(null);

  const selectedReactor = useMemo(
    () => reactors.find((item) => item.reactor_id === selectedReactorId) ?? null,
    [reactors, selectedReactorId],
  );

  const selectedDevices = useMemo(
    () => devices.filter((device) => device.reactor_id === selectedReactorId),
    [devices, selectedReactorId],
  );

  async function loadOverview(preferredReactorId?: number | null) {
    setLoading(true);
    setPageError(null);
    try {
      const [reactorData, deviceData, bridgeStatus] = await Promise.all([
        apiRequest<ReactorTwin[]>('/api/v1/reactor-ops'),
        apiRequest<DeviceNode[]>('/api/v1/devices'),
        apiRequest<MQTTBridgeStatus>('/api/v1/reactor-control/mqtt-status').catch(() => null),
      ]);
      setReactors(reactorData);
      setDevices(deviceData);
      setMqttStatus(bridgeStatus);
      const nextSelectedId =
        preferredReactorId && reactorData.some((item) => item.reactor_id === preferredReactorId)
          ? preferredReactorId
          : selectedReactorId && reactorData.some((item) => item.reactor_id === selectedReactorId)
            ? selectedReactorId
            : reactorData[0]?.reactor_id ?? null;
      setSelectedReactorId(nextSelectedId);
      if (nextSelectedId !== null) {
        await loadReactorControl(nextSelectedId);
      }
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function loadReactorControl(reactorId: number) {
    setDetailLoading(true);
    setSetpointError(null);
    try {
      const [latest, history, nextSetpoints, nextCommands] = await Promise.all([
        apiRequest<TelemetryValue[]>(`/api/v1/reactors/${reactorId}/telemetry/latest`),
        apiRequest<TelemetryValue[]>(`/api/v1/reactors/${reactorId}/telemetry?limit=20`),
        apiRequest<ReactorSetpoint[]>(`/api/v1/reactors/${reactorId}/setpoints`),
        apiRequest<ReactorCommand[]>(`/api/v1/reactors/${reactorId}/commands`),
      ]);
      setLatestTelemetry(latest);
      setTelemetryHistory(history);
      setSetpoints(nextSetpoints);
      setCommands(nextCommands);
      setEditSetpointForms(
        Object.fromEntries(nextSetpoints.map((setpoint) => [setpoint.id, toEditSetpointFormState(setpoint)])) as Record<
          number,
          EditSetpointFormState
        >,
      );
      setCreateSetpointForm(createSetpointFormState());
      setSelectedReactorId(reactorId);
    } catch (error) {
      setSetpointError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  useEffect(() => {
    void loadOverview();
  }, []);

  function setCreateSetpointValue<Key extends keyof CreateSetpointFormState>(
    key: Key,
    value: CreateSetpointFormState[Key],
  ) {
    setCreateSetpointForm((current) => ({ ...current, [key]: value }));
  }

  function setEditSetpointValue<Key extends keyof EditSetpointFormState>(
    setpointId: number,
    key: Key,
    value: EditSetpointFormState[Key],
  ) {
    setEditSetpointForms((current) => ({
      ...current,
      [setpointId]: {
        ...(current[setpointId] ?? {
          target_value: '',
          min_value: '',
          max_value: '',
          mode: 'manual',
        }),
        [key]: value,
      },
    }));
  }

  async function handleCreateSetpoint(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedReactorId) {
      return;
    }
    setCreatingSetpoint(true);
    setSetpointError(null);
    setNotice(null);
    try {
      await apiRequest(`/api/v1/reactors/${selectedReactorId}/setpoints`, {
        method: 'POST',
        body: JSON.stringify({
          parameter: createSetpointForm.parameter,
          target_value: Number(createSetpointForm.target_value),
          min_value: toNumberOrNull(createSetpointForm.min_value),
          max_value: toNumberOrNull(createSetpointForm.max_value),
          mode: createSetpointForm.mode,
        }),
      });
      setNotice('Setpoint angelegt.');
      await loadReactorControl(selectedReactorId);
    } catch (error) {
      setSetpointError(getErrorMessage(error));
    } finally {
      setCreatingSetpoint(false);
    }
  }

  async function handleSaveSetpoint(setpoint: ReactorSetpoint) {
    const draft = editSetpointForms[setpoint.id];
    if (!draft) {
      return;
    }
    setSavingSetpointId(setpoint.id);
    setSetpointError(null);
    setNotice(null);
    try {
      await apiRequest(`/api/v1/setpoints/${setpoint.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          target_value: Number(draft.target_value),
          min_value: toNumberOrNull(draft.min_value),
          max_value: toNumberOrNull(draft.max_value),
          mode: draft.mode,
        }),
      });
      setNotice(`Setpoint ${setpoint.parameter} aktualisiert.`);
      if (selectedReactorId !== null) {
        await loadReactorControl(selectedReactorId);
      }
    } catch (error) {
      setSetpointError(getErrorMessage(error));
    } finally {
      setSavingSetpointId(null);
    }
  }

  async function handleSendCommand(commandType: ReactorCommandType) {
    if (!selectedReactorId) {
      return;
    }
    setSendingCommand(commandType);
    setNotice(null);
    setSetpointError(null);
    try {
      const command = await apiRequest<ReactorCommand>(`/api/v1/reactors/${selectedReactorId}/commands`, {
        method: 'POST',
        body: JSON.stringify({ command_type: commandType }),
      });
      if (command.status === 'sent') {
        setNotice(`Command ${commandType} in MQTT publiziert.`);
      } else if (command.status === 'failed') {
        setNotice(`Command ${commandType} gespeichert, MQTT-Publish aber fehlgeschlagen.`);
      } else {
        setNotice(`Command ${commandType} als Stub in die Queue gelegt.`);
      }
      await loadReactorControl(selectedReactorId);
    } catch (error) {
      setSetpointError(getErrorMessage(error));
    } finally {
      setSendingCommand(null);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Reactor Control / Telemetry</h1>
        <p className="muted">
          Ist-Werte, DeviceNodes, Setpoints, MQTT-Bridge und vorbereitete Control-Commands als Bruecke zwischen ReactorOps-Soll und spaeterer Hardwareintegration.
        </p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="MQTT Bridge">
          <div className="stackCompact">
            <div>
              <strong>Status:</strong>{' '}
              <span className={`badge badge-${mqttStatus?.connected ? 'online' : 'offline'}`}>
                {mqttStatus?.enabled ? (mqttStatus.connected ? 'connected' : 'disconnected') : 'disabled'}
              </span>
            </div>
            <div className="muted">
              Broker: {mqttStatus ? `${mqttStatus.broker_host}:${mqttStatus.broker_port}` : 'n/a'} · Prefix:{' '}
              {mqttStatus?.topic_prefix || 'n/a'}
            </div>
            <div className="muted">
              Publish: {mqttStatus?.publish_commands ? 'aktiv' : 'deaktiviert'} · Letzte Nachricht:{' '}
              {formatDateTime(mqttStatus?.last_message_at || null)}
            </div>
            {mqttStatus?.last_error ? <InlineMessage tone="error">{mqttStatus.last_error}</InlineMessage> : null}
          </div>
        </Card>

        <Card title="Reaktoren">
          {loading ? (
            <InlineMessage>Lade Reactor Control Daten…</InlineMessage>
          ) : reactors.length === 0 ? (
            <p className="muted">Noch keine Reaktoren vorhanden.</p>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Reaktor</th>
                    <th>Phase</th>
                    <th>Tech</th>
                    <th>Nodes</th>
                  </tr>
                </thead>
                <tbody>
                  {reactors.map((reactor) => {
                    const nodeCount = devices.filter((device) => device.reactor_id === reactor.reactor_id).length;
                    return (
                      <tr key={reactor.reactor_id}>
                        <td>
                          <button className="linkButton" type="button" onClick={() => void loadReactorControl(reactor.reactor_id)}>
                            <div className="stackCompact">
                              <strong>{reactor.reactor_name}</strong>
                              <span className="muted">{reactor.current_charge?.name || reactor.culture_type || reactor.reactor_type}</span>
                            </div>
                          </button>
                        </td>
                        <td><span className={`badge badge-${reactor.current_phase}`}>{reactor.current_phase}</span></td>
                        <td><span className={`badge badge-${reactor.technical_state}`}>{reactor.technical_state}</span></td>
                        <td>{nodeCount}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title={selectedReactor ? `${selectedReactor.reactor_name} Ist-Werte` : 'Ist-Werte'}>
          {detailLoading ? <InlineMessage>Lade Reaktorwerte…</InlineMessage> : null}
          {selectedReactor ? (
            <div className="grid cols-3">
              {telemetrySensorTypeOptions.slice(0, 4).map((option) => {
                const latest = latestTelemetry.find((value) => value.sensor_type === option.value);
                return (
                  <Card key={option.value} title={option.label}>
                    <div className="kpi" style={{ fontSize: '1.4rem' }}>
                      {latest ? `${latest.value} ${latest.unit}` : 'n/a'}
                    </div>
                    <p className="muted">{latest ? `${latest.source} · ${formatDateTime(latest.timestamp)}` : 'Noch kein Telemetry-Wert'}</p>
                  </Card>
                );
              })}
            </div>
          ) : (
            <p className="muted">Waehle einen Reaktor aus.</p>
          )}
        </Card>
      </div>

      {selectedReactor ? (
        <>
          <div className="grid cols-2">
            <Card title="Letzte Telemetry">
              <div className="buttonRow">
                <a className="button buttonSecondary" href="/reactor-ops">Zu ReactorOps</a>
                <a className="button buttonSecondary" href="/sensors">Zu Sensorik</a>
              </div>
              {telemetryHistory.length === 0 ? (
                <p className="muted">Noch keine Telemetry fuer diesen Reaktor vorhanden.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Parameter</th>
                        <th>Wert</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {telemetryHistory.map((value) => (
                        <tr key={value.id}>
                          <td>{formatDateTime(value.timestamp)}</td>
                          <td>{getOptionLabel(telemetrySensorTypeOptions, value.sensor_type)}</td>
                          <td>{value.value} {value.unit}</td>
                          <td><span className={`badge badge-${value.source}`}>{value.source}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Devices / Nodes">
              {selectedDevices.length === 0 ? (
                <p className="muted">Keine DeviceNodes diesem Reaktor zugeordnet.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Node ID</th>
                        <th>Typ</th>
                        <th>Status</th>
                        <th>Last Seen</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedDevices.map((device) => (
                        <tr key={device.id}>
                          <td>
                            <div className="stackCompact">
                              <strong>{device.name}</strong>
                              <span className="muted">{device.firmware_version || 'ohne Firmware-Info'}</span>
                            </div>
                          </td>
                          <td>{device.node_id || 'n/a'}</td>
                          <td>{getOptionLabel(deviceNodeTypeOptions, device.node_type)}</td>
                          <td><span className={`badge badge-${device.status}`}>{device.status}</span></td>
                          <td>{formatDateTime(device.last_seen_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>

          <div className="grid cols-2">
            <Card title="Setpoints">
              {setpointError ? <InlineMessage tone="error">{setpointError}</InlineMessage> : null}
              {setpoints.length === 0 ? (
                <p className="muted">Noch keine Setpoints fuer diesen Reaktor gesetzt.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Parameter</th>
                        <th>Target</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Mode</th>
                        <th>Aktion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {setpoints.map((setpoint) => {
                        const draft = editSetpointForms[setpoint.id];
                        return (
                          <tr key={setpoint.id}>
                            <td>{getOptionLabel(reactorControlParameterOptions, setpoint.parameter)}</td>
                            <td>
                              <input
                                className="input inputCompact"
                                type="number"
                                step="0.1"
                                value={draft?.target_value ?? ''}
                                onChange={(event) => setEditSetpointValue(setpoint.id, 'target_value', event.target.value)}
                                disabled={!canEdit}
                              />
                            </td>
                            <td>
                              <input
                                className="input inputCompact"
                                type="number"
                                step="0.1"
                                value={draft?.min_value ?? ''}
                                onChange={(event) => setEditSetpointValue(setpoint.id, 'min_value', event.target.value)}
                                disabled={!canEdit}
                              />
                            </td>
                            <td>
                              <input
                                className="input inputCompact"
                                type="number"
                                step="0.1"
                                value={draft?.max_value ?? ''}
                                onChange={(event) => setEditSetpointValue(setpoint.id, 'max_value', event.target.value)}
                                disabled={!canEdit}
                              />
                            </td>
                            <td>
                              <select
                                className="input inputCompact"
                                value={draft?.mode ?? 'manual'}
                                onChange={(event) => setEditSetpointValue(setpoint.id, 'mode', event.target.value as ReactorSetpointMode)}
                                disabled={!canEdit}
                              >
                                {reactorSetpointModeOptions.map((option) => (
                                  <option key={option.value} value={option.value}>
                                    {option.label}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td>
                              {canEdit ? (
                                <button
                                  className="button buttonSecondary buttonCompact"
                                  type="button"
                                  disabled={savingSetpointId === setpoint.id}
                                  onClick={() => void handleSaveSetpoint(setpoint)}
                                >
                                  {savingSetpointId === setpoint.id ? 'Speichert…' : 'Speichern'}
                                </button>
                              ) : (
                                <span className="muted">read-only</span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              <form className="entityForm" onSubmit={handleCreateSetpoint}>
                <div className="formGrid">
                  <FormField label="Neuer Parameter">
                    <select
                      className="input"
                      value={createSetpointForm.parameter}
                      onChange={(event) => setCreateSetpointValue('parameter', event.target.value as ReactorControlParameter)}
                      disabled={!canEdit}
                    >
                      {reactorControlParameterOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Mode">
                    <select
                      className="input"
                      value={createSetpointForm.mode}
                      onChange={(event) => setCreateSetpointValue('mode', event.target.value as ReactorSetpointMode)}
                      disabled={!canEdit}
                    >
                      {reactorSetpointModeOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormField>

                  <FormField label="Target">
                    <input className="input" type="number" step="0.1" value={createSetpointForm.target_value} onChange={(event) => setCreateSetpointValue('target_value', event.target.value)} disabled={!canEdit} required />
                  </FormField>

                  <FormField label="Min">
                    <input className="input" type="number" step="0.1" value={createSetpointForm.min_value} onChange={(event) => setCreateSetpointValue('min_value', event.target.value)} disabled={!canEdit} />
                  </FormField>

                  <FormField label="Max">
                    <input className="input" type="number" step="0.1" value={createSetpointForm.max_value} onChange={(event) => setCreateSetpointValue('max_value', event.target.value)} disabled={!canEdit} />
                  </FormField>
                </div>

                {canEdit ? (
                  <div className="buttonRow">
                    <button className="button" type="submit" disabled={creatingSetpoint}>
                      {creatingSetpoint ? 'Legt an…' : 'Setpoint anlegen'}
                    </button>
                  </div>
                ) : (
                  <p className="muted">Viewer sehen Setpoints read-only.</p>
                )}
              </form>
            </Card>

            <Card title="Command Stub Queue">
              <div className="buttonRow">
                {reactorCommandTypeOptions.map((option) => (
                  <button
                    key={option.value}
                    className="button buttonSecondary"
                    type="button"
                    disabled={!canEdit || sendingCommand === option.value}
                    onClick={() => void handleSendCommand(option.value)}
                  >
                    {sendingCommand === option.value ? 'Sende…' : option.label}
                  </button>
                ))}
              </div>

              {commands.length === 0 ? (
                <p className="muted">Noch keine Commands fuer diesen Reaktor geloggt.</p>
              ) : (
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Zeitpunkt</th>
                        <th>Command</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {commands.map((command) => (
                        <tr key={command.id}>
                          <td>{formatDateTime(command.created_at)}</td>
                          <td>{getOptionLabel(reactorCommandTypeOptions, command.command_type)}</td>
                          <td><span className={`badge badge-${command.status}`}>{command.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
