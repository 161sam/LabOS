'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import {
  Reactor,
  Sensor,
  SensorStatus,
  SensorType,
  SensorValue,
  sensorStatusOptions,
  sensorTypeOptions,
} from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

type SensorFormState = {
  name: string;
  sensor_type: SensorType;
  unit: string;
  status: SensorStatus;
  reactor_id: string;
  location: string;
  notes: string;
};

type SensorValueFormState = {
  value: string;
  recorded_at: string;
  source: string;
};

function createEmptySensorForm(): SensorFormState {
  return {
    name: '',
    sensor_type: 'temperature',
    unit: '°C',
    status: 'active',
    reactor_id: '',
    location: '',
    notes: '',
  };
}

function createEmptyValueForm(): SensorValueFormState {
  return {
    value: '',
    recorded_at: '',
    source: 'manual',
  };
}

function toSensorFormState(sensor: Sensor): SensorFormState {
  return {
    name: sensor.name,
    sensor_type: sensor.sensor_type,
    unit: sensor.unit,
    status: sensor.status,
    reactor_id: sensor.reactor_id ? String(sensor.reactor_id) : '',
    location: sensor.location ?? '',
    notes: sensor.notes ?? '',
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
    return 'Nicht vorhanden';
  }

  return new Date(value).toLocaleString('de-DE');
}

function formatValue(sensor: Sensor, value: number | null) {
  if (value === null) {
    return 'Noch kein Wert';
  }

  return `${value} ${sensor.unit}`;
}

export function SensorManager() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [values, setValues] = useState<SensorValue[]>([]);
  const [form, setForm] = useState<SensorFormState>(createEmptySensorForm);
  const [valueForm, setValueForm] = useState<SensorValueFormState>(createEmptyValueForm);
  const [statusDrafts, setStatusDrafts] = useState<Record<number, SensorStatus>>({});
  const [loading, setLoading] = useState(true);
  const [valuesLoading, setValuesLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [valueSubmitting, setValueSubmitting] = useState(false);
  const [statusSavingId, setStatusSavingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [valueError, setValueError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<'create' | 'edit'>('create');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedSensorId, setSelectedSensorId] = useState<number | null>(null);

  const selectedSensor = sensors.find((sensor) => sensor.id === selectedSensorId) ?? null;

  async function loadValues(sensorId: number) {
    setValuesLoading(true);
    setValueError(null);

    try {
      const sensorValues = await apiRequest<SensorValue[]>(`/api/v1/sensors/${sensorId}/values?limit=20`);
      setValues(sensorValues);
    } catch (error) {
      setValueError(getErrorMessage(error));
    } finally {
      setValuesLoading(false);
    }
  }

  async function loadData(preferredSensorId?: number | null) {
    setLoading(true);
    setPageError(null);

    try {
      const [sensorData, reactorData] = await Promise.all([
        apiRequest<Sensor[]>('/api/v1/sensors'),
        apiRequest<Reactor[]>('/api/v1/reactors'),
      ]);

      setSensors(sensorData);
      setReactors(reactorData);
      setStatusDrafts(
        Object.fromEntries(sensorData.map((sensor) => [sensor.id, sensor.status])) as Record<number, SensorStatus>,
      );

      if (sensorData.length === 0) {
        setSelectedSensorId(null);
        setValues([]);
        return;
      }

      const desiredSensorId =
        preferredSensorId && sensorData.some((sensor) => sensor.id === preferredSensorId)
          ? preferredSensorId
          : selectedSensorId && sensorData.some((sensor) => sensor.id === selectedSensorId)
            ? selectedSensorId
            : sensorData[0].id;

      setSelectedSensorId(desiredSensorId);
      await loadValues(desiredSensorId);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function resetForm() {
    setMode('create');
    setEditingId(null);
    setForm(createEmptySensorForm());
    setFormError(null);
  }

  function setFormValue<Key extends keyof SensorFormState>(key: Key, value: SensorFormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function setValueFormValue<Key extends keyof SensorValueFormState>(key: Key, value: SensorValueFormState[Key]) {
    setValueForm((current) => ({ ...current, [key]: value }));
  }

  async function startEdit(sensorId: number) {
    setDetailLoading(true);
    setFormError(null);
    setNotice(null);

    try {
      const sensor = await apiRequest<Sensor>(`/api/v1/sensors/${sensorId}`);
      setForm(toSensorFormState(sensor));
      setMode('edit');
      setEditingId(sensor.id);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  async function selectSensor(sensorId: number) {
    setSelectedSensorId(sensorId);
    await loadValues(sensorId);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setNotice(null);

    const payload = {
      name: form.name,
      sensor_type: form.sensor_type,
      unit: form.unit,
      status: form.status,
      reactor_id: form.reactor_id ? Number(form.reactor_id) : null,
      location: form.location,
      notes: form.notes,
    };

    try {
      if (mode === 'create') {
        const created = await apiRequest<Sensor>('/api/v1/sensors', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setNotice('Sensor angelegt.');
        resetForm();
        await loadData(created.id);
      } else if (editingId !== null) {
        const updated = await apiRequest<Sensor>(`/api/v1/sensors/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setNotice('Sensor aktualisiert.');
        resetForm();
        await loadData(updated.id);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(sensor: Sensor) {
    const nextStatus = statusDrafts[sensor.id] ?? sensor.status;
    if (nextStatus === sensor.status) {
      return;
    }

    setStatusSavingId(sensor.id);
    setPageError(null);
    setNotice(null);

    try {
      const updated = await apiRequest<Sensor>(`/api/v1/sensors/${sensor.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      setNotice(`Status von ${updated.name} aktualisiert.`);
      await loadData(updated.id);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setStatusSavingId(null);
    }
  }

  async function handleValueSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedSensorId) {
      return;
    }

    setValueSubmitting(true);
    setValueError(null);
    setNotice(null);

    const payload = {
      value: Number(valueForm.value),
      recorded_at: valueForm.recorded_at || null,
      source: valueForm.source || null,
    };

    try {
      await apiRequest<SensorValue>(`/api/v1/sensors/${selectedSensorId}/values`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setNotice('Sensorwert gespeichert.');
      setValueForm(createEmptyValueForm());
      await loadData(selectedSensorId);
    } catch (error) {
      setValueError(getErrorMessage(error));
    } finally {
      setValueSubmitting(false);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Sensoren</h1>
        <p className="muted">Sensoren verwalten, Messwerte manuell einspeisen und den letzten Verlauf direkt im LabOS pruefen.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title={mode === 'create' ? 'Neuer Sensor' : `Sensor bearbeiten #${editingId}`}>
          {detailLoading ? <InlineMessage>Lade Sensor…</InlineMessage> : null}
          {formError ? <InlineMessage tone="error">{formError}</InlineMessage> : null}

          <form className="entityForm" onSubmit={handleSubmit}>
            <div className="formGrid">
              <FormField label="Name">
                <input className="input" value={form.name} onChange={(event) => setFormValue('name', event.target.value)} required />
              </FormField>

              <FormField label="Sensortyp">
                <select
                  className="input"
                  value={form.sensor_type}
                  onChange={(event) => setFormValue('sensor_type', event.target.value as SensorType)}
                >
                  {sensorTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Einheit">
                <input className="input" value={form.unit} onChange={(event) => setFormValue('unit', event.target.value)} required />
              </FormField>

              <FormField label="Status">
                <select
                  className="input"
                  value={form.status}
                  onChange={(event) => setFormValue('status', event.target.value as SensorStatus)}
                >
                  {sensorStatusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Reaktor">
                <select
                  className="input"
                  value={form.reactor_id}
                  onChange={(event) => setFormValue('reactor_id', event.target.value)}
                >
                  <option value="">Nicht zugeordnet</option>
                  {reactors.map((reactor) => (
                    <option key={reactor.id} value={reactor.id}>
                      {reactor.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Standort">
                <input className="input" value={form.location} onChange={(event) => setFormValue('location', event.target.value)} />
              </FormField>
            </div>

            <FormField label="Notizen">
              <textarea className="input textarea" rows={5} value={form.notes} onChange={(event) => setFormValue('notes', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={submitting}>
                {submitting ? 'Speichert…' : mode === 'create' ? 'Sensor anlegen' : 'Sensor speichern'}
              </button>
              {mode === 'edit' ? (
                <button className="button buttonSecondary" type="button" onClick={resetForm}>
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card title="Sensoruebersicht">
          {loading ? (
            <InlineMessage>Lade Sensoren…</InlineMessage>
          ) : sensors.length === 0 ? (
            <InlineMessage>Noch keine Sensoren vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Typ</th>
                    <th>Reaktor / Ort</th>
                    <th>Status</th>
                    <th>Letzter Wert</th>
                    <th>Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {sensors.map((sensor) => (
                    <tr key={sensor.id}>
                      <td>{sensor.name}</td>
                      <td>{sensor.sensor_type}</td>
                      <td>{sensor.reactor_name || sensor.location || 'Nicht zugeordnet'}</td>
                      <td>
                        <div className="statusControl">
                          <select
                            className="input inputCompact"
                            value={statusDrafts[sensor.id] ?? sensor.status}
                            onChange={(event) =>
                              setStatusDrafts((current) => ({
                                ...current,
                                [sensor.id]: event.target.value as SensorStatus,
                              }))
                            }
                          >
                            {sensorStatusOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="button buttonSecondary buttonCompact"
                            type="button"
                            disabled={statusSavingId === sensor.id}
                            onClick={() => void handleStatusUpdate(sensor)}
                          >
                            {statusSavingId === sensor.id ? '...' : 'Setzen'}
                          </button>
                        </div>
                      </td>
                      <td>
                        <div className="stackCompact">
                          <span>{formatValue(sensor, sensor.last_value)}</span>
                          <span className="muted">{formatDateTime(sensor.last_recorded_at)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="buttonRow">
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void startEdit(sensor.id)}>
                            Bearbeiten
                          </button>
                          <button className="button buttonSecondary buttonCompact" type="button" onClick={() => void selectSensor(sensor.id)}>
                            Verlauf
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
      </div>

      <div className="grid cols-2">
        <Card title={selectedSensor ? `Werte fuer ${selectedSensor.name}` : 'Sensorwerte'}>
          {!selectedSensor ? (
            <InlineMessage>Waehle einen Sensor aus der Liste, um Werte zu sehen oder hinzuzufuegen.</InlineMessage>
          ) : (
            <div className="stackBlock">
              <div className="detailList">
                <div className="detailRow">
                  <span className="muted">Zuordnung</span>
                  <strong>{selectedSensor.reactor_name || selectedSensor.location || 'Nicht zugeordnet'}</strong>
                </div>
                <div className="detailRow">
                  <span className="muted">Letzter Wert</span>
                  <strong>{formatValue(selectedSensor, selectedSensor.last_value)}</strong>
                </div>
                <div className="detailRow">
                  <span className="muted">Letzte Messung</span>
                  <strong>{formatDateTime(selectedSensor.last_recorded_at)}</strong>
                </div>
              </div>

              {valueError ? <InlineMessage tone="error">{valueError}</InlineMessage> : null}

              <form className="entityForm" onSubmit={handleValueSubmit}>
                <div className="formGrid">
                  <FormField label={`Wert (${selectedSensor.unit})`}>
                    <input
                      className="input"
                      type="number"
                      step="0.1"
                      value={valueForm.value}
                      onChange={(event) => setValueFormValue('value', event.target.value)}
                      required
                    />
                  </FormField>

                  <FormField label="Quelle">
                    <input
                      className="input"
                      value={valueForm.source}
                      onChange={(event) => setValueFormValue('source', event.target.value)}
                    />
                  </FormField>

                  <FormField label="Zeitpunkt (optional)">
                    <input
                      className="input"
                      type="datetime-local"
                      value={valueForm.recorded_at}
                      onChange={(event) => setValueFormValue('recorded_at', event.target.value)}
                    />
                  </FormField>
                </div>

                <div className="buttonRow">
                  <button className="button" type="submit" disabled={valueSubmitting}>
                    {valueSubmitting ? 'Speichert…' : 'Sensorwert erfassen'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </Card>

        <Card title="Verlauf">
          {!selectedSensor ? (
            <InlineMessage>Kein Sensor ausgewaehlt.</InlineMessage>
          ) : valuesLoading ? (
            <InlineMessage>Lade Verlauf…</InlineMessage>
          ) : values.length === 0 ? (
            <InlineMessage>Noch keine Messwerte fuer diesen Sensor vorhanden.</InlineMessage>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Zeitpunkt</th>
                    <th>Wert</th>
                    <th>Quelle</th>
                  </tr>
                </thead>
                <tbody>
                  {values.map((value) => (
                    <tr key={value.id}>
                      <td>{formatDateTime(value.recorded_at)}</td>
                      <td>{`${value.value} ${selectedSensor.unit}`}</td>
                      <td>{value.source || 'Nicht gesetzt'}</td>
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
