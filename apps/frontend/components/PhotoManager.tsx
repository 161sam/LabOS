'use client';

import { FormEvent, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { Charge, Photo, PhotoAnalysisStatus, Reactor } from '../lib/lab-resources';
import { Card } from './Card';
import { FormField } from './FormField';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type UploadFormState = {
  file: File | null;
  title: string;
  notes: string;
  charge_id: string;
  reactor_id: string;
  uploaded_by: string;
  captured_at: string;
};

type PhotoFilters = {
  charge_id: string;
  reactor_id: string;
};

type EditFormState = {
  title: string;
  notes: string;
  charge_id: string;
  reactor_id: string;
  uploaded_by: string;
  captured_at: string;
};

function createEmptyUploadForm(): UploadFormState {
  return {
    file: null,
    title: '',
    notes: '',
    charge_id: '',
    reactor_id: '',
    uploaded_by: '',
    captured_at: '',
  };
}

function createEditForm(photo: Photo | null): EditFormState {
  return {
    title: photo?.title ?? '',
    notes: photo?.notes ?? '',
    charge_id: photo?.charge_id ? String(photo.charge_id) : '',
    reactor_id: photo?.reactor_id ? String(photo.reactor_id) : '',
    uploaded_by: photo?.uploaded_by ?? '',
    captured_at: photo?.captured_at ? photo.captured_at.slice(0, 16) : '',
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
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

function formatSize(sizeBytes: number) {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }
  if (sizeBytes < 1024 * 1024) {
    return `${(sizeBytes / 1024).toFixed(1)} KB`;
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function PhotoManager() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [charges, setCharges] = useState<Charge[]>([]);
  const [reactors, setReactors] = useState<Reactor[]>([]);
  const [filters, setFilters] = useState<PhotoFilters>({ charge_id: '', reactor_id: '' });
  const [uploadForm, setUploadForm] = useState<UploadFormState>(createEmptyUploadForm);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>(createEditForm(null));
  const [analysisStatus, setAnalysisStatus] = useState<PhotoAnalysisStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadData(nextFilters: PhotoFilters = filters, preferredPhotoId?: number | null) {
    setLoading(true);
    setPageError(null);

    const params = new URLSearchParams();
    if (nextFilters.charge_id) params.set('charge_id', nextFilters.charge_id);
    if (nextFilters.reactor_id) params.set('reactor_id', nextFilters.reactor_id);
    const photoPath = params.size > 0 ? `/api/v1/photos?${params.toString()}` : '/api/v1/photos';

    try {
      const [photoData, chargeData, reactorData] = await Promise.all([
        apiRequest<Photo[]>(photoPath),
        apiRequest<Charge[]>('/api/v1/charges'),
        apiRequest<Reactor[]>('/api/v1/reactors'),
      ]);
      setPhotos(photoData);
      setCharges(chargeData);
      setReactors(reactorData);

      if (photoData.length === 0) {
        setSelectedPhoto(null);
        setEditForm(createEditForm(null));
        setAnalysisStatus(null);
        return;
      }

      const desiredPhotoId =
        preferredPhotoId && photoData.some((photo) => photo.id === preferredPhotoId)
          ? preferredPhotoId
          : selectedPhoto && photoData.some((photo) => photo.id === selectedPhoto.id)
            ? selectedPhoto.id
            : photoData[0].id;

      await selectPhoto(desiredPhotoId);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData(filters);
  }, []);

  async function selectPhoto(photoId: number) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const [photo, analysis] = await Promise.all([
        apiRequest<Photo>(`/api/v1/photos/${photoId}`),
        apiRequest<PhotoAnalysisStatus>(`/api/v1/photos/${photoId}/analysis-status`),
      ]);
      setSelectedPhoto(photo);
      setEditForm(createEditForm(photo));
      setAnalysisStatus(analysis);
    } catch (error) {
      setDetailError(getErrorMessage(error));
    } finally {
      setDetailLoading(false);
    }
  }

  function setUploadValue<Key extends keyof UploadFormState>(key: Key, value: UploadFormState[Key]) {
    setUploadForm((current) => ({ ...current, [key]: value }));
  }

  function setEditValue<Key extends keyof EditFormState>(key: Key, value: EditFormState[Key]) {
    setEditForm((current) => ({ ...current, [key]: value }));
  }

  async function applyFilters(nextFilters: PhotoFilters) {
    setFilters(nextFilters);
    await loadData(nextFilters);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!uploadForm.file) {
      setUploadError('Bitte zuerst eine Bilddatei auswaehlen.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setNotice(null);

    const formData = new FormData();
    formData.append('file', uploadForm.file);
    if (uploadForm.title) formData.append('title', uploadForm.title);
    if (uploadForm.notes) formData.append('notes', uploadForm.notes);
    if (uploadForm.charge_id) formData.append('charge_id', uploadForm.charge_id);
    if (uploadForm.reactor_id) formData.append('reactor_id', uploadForm.reactor_id);
    if (uploadForm.uploaded_by) formData.append('uploaded_by', uploadForm.uploaded_by);
    if (uploadForm.captured_at) formData.append('captured_at', uploadForm.captured_at);

    try {
      const created = await apiRequest<Photo>('/api/v1/photos/upload', {
        method: 'POST',
        body: formData,
      });
      setUploadForm(createEmptyUploadForm());
      setNotice('Foto hochgeladen.');
      await loadData(filters, created.id);
    } catch (error) {
      setUploadError(getErrorMessage(error));
    } finally {
      setUploading(false);
    }
  }

  async function handleMetadataSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPhoto) {
      return;
    }

    setSaving(true);
    setDetailError(null);
    setNotice(null);

    try {
      const updated = await apiRequest<Photo>(`/api/v1/photos/${selectedPhoto.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: editForm.title,
          notes: editForm.notes,
          charge_id: editForm.charge_id ? Number(editForm.charge_id) : null,
          reactor_id: editForm.reactor_id ? Number(editForm.reactor_id) : null,
          uploaded_by: editForm.uploaded_by,
          captured_at: editForm.captured_at || null,
        }),
      });
      setNotice('Foto-Metadaten gespeichert.');
      await loadData(filters, updated.id);
    } catch (error) {
      setDetailError(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Fotos</h1>
        <p className="muted">Visuelle Labor-Dokumentation fuer Charges, Reaktoren und spaetere Vision-Auswertung lokal erfassen.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
      {notice ? <InlineMessage tone="success">{notice}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title="Foto hochladen">
          {uploadError ? <InlineMessage tone="error">{uploadError}</InlineMessage> : null}
          <form className="entityForm" onSubmit={handleUpload}>
            <div className="formGrid">
              <FormField label="Bilddatei">
                <input
                  className="input"
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={(event) => setUploadValue('file', event.target.files?.[0] ?? null)}
                  required
                />
              </FormField>

              <FormField label="Aufgenommen am">
                <input
                  className="input"
                  type="datetime-local"
                  value={uploadForm.captured_at}
                  onChange={(event) => setUploadValue('captured_at', event.target.value)}
                />
              </FormField>

              <FormField label="Titel">
                <input className="input" value={uploadForm.title} onChange={(event) => setUploadValue('title', event.target.value)} />
              </FormField>

              <FormField label="Hochgeladen von">
                <input className="input" value={uploadForm.uploaded_by} onChange={(event) => setUploadValue('uploaded_by', event.target.value)} />
              </FormField>

              <FormField label="Charge">
                <select className="input" value={uploadForm.charge_id} onChange={(event) => setUploadValue('charge_id', event.target.value)}>
                  <option value="">Nicht zugeordnet</option>
                  {charges.map((charge) => (
                    <option key={charge.id} value={charge.id}>
                      {charge.name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Reaktor">
                <select className="input" value={uploadForm.reactor_id} onChange={(event) => setUploadValue('reactor_id', event.target.value)}>
                  <option value="">Nicht zugeordnet</option>
                  {reactors.map((reactor) => (
                    <option key={reactor.id} value={reactor.id}>
                      {reactor.name}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>

            <FormField label="Notiz">
              <textarea className="input textarea" rows={4} value={uploadForm.notes} onChange={(event) => setUploadValue('notes', event.target.value)} />
            </FormField>

            <div className="buttonRow">
              <button className="button" type="submit" disabled={uploading}>
                {uploading ? 'Laedt hoch…' : 'Foto hochladen'}
              </button>
            </div>
          </form>
        </Card>

        <Card title="Foto-Historie">
          <div className="formGrid">
            <FormField label="Charge-Filter">
              <select className="input" value={filters.charge_id} onChange={(event) => void applyFilters({ ...filters, charge_id: event.target.value })}>
                <option value="">Alle</option>
                {charges.map((charge) => (
                  <option key={charge.id} value={charge.id}>
                    {charge.name}
                  </option>
                ))}
              </select>
            </FormField>

            <FormField label="Reaktor-Filter">
              <select className="input" value={filters.reactor_id} onChange={(event) => void applyFilters({ ...filters, reactor_id: event.target.value })}>
                <option value="">Alle</option>
                {reactors.map((reactor) => (
                  <option key={reactor.id} value={reactor.id}>
                    {reactor.name}
                  </option>
                ))}
              </select>
            </FormField>
          </div>

          {loading ? (
            <InlineMessage>Lade Fotos…</InlineMessage>
          ) : photos.length === 0 ? (
            <InlineMessage>Keine Fotos fuer den aktuellen Filter vorhanden.</InlineMessage>
          ) : (
            <div className="photoGrid">
              {photos.map((photo) => (
                <button
                  key={photo.id}
                  className="photoTile"
                  type="button"
                  onClick={() => void selectPhoto(photo.id)}
                >
                  <img className="photoThumb" src={`${apiBase}${photo.file_url}`} alt={photo.title || photo.original_filename} />
                  <div className="photoMeta">
                    <strong>{photo.title || photo.original_filename}</strong>
                    <span className="muted">{formatDateTime(photo.captured_at || photo.created_at)}</span>
                    <span className="muted">{photo.charge_name || photo.reactor_name || 'Nicht zugeordnet'}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card title={selectedPhoto ? `Foto-Details #${selectedPhoto.id}` : 'Foto-Details'}>
        {detailLoading ? <InlineMessage>Lade Foto…</InlineMessage> : null}
        {detailError ? <InlineMessage tone="error">{detailError}</InlineMessage> : null}

        {!selectedPhoto && !detailLoading ? (
          <InlineMessage>Waehle ein Foto aus der Historie, um Metadaten und die Detailansicht zu sehen.</InlineMessage>
        ) : selectedPhoto ? (
          <div className="grid cols-2">
            <div className="stackBlock">
              <img className="detailMedia" src={`${apiBase}${selectedPhoto.file_url}`} alt={selectedPhoto.title || selectedPhoto.original_filename} />
              <div className="detailList">
                <div className="detailRow"><strong>Datei</strong><span>{selectedPhoto.original_filename}</span></div>
                <div className="detailRow"><strong>Typ</strong><span>{selectedPhoto.mime_type}</span></div>
                <div className="detailRow"><strong>Groesse</strong><span>{formatSize(selectedPhoto.size_bytes)}</span></div>
                <div className="detailRow"><strong>Erstellt</strong><span>{formatDateTime(selectedPhoto.created_at)}</span></div>
                <div className="detailRow"><strong>Vision-Status</strong><span>{analysisStatus?.status ?? 'pending'}</span></div>
              </div>
              <InlineMessage>{analysisStatus?.detail ?? 'Vision-Auswertung wird spaeter angebunden.'}</InlineMessage>
            </div>

            <form className="entityForm" onSubmit={handleMetadataSave}>
              <div className="formGrid">
                <FormField label="Titel">
                  <input className="input" value={editForm.title} onChange={(event) => setEditValue('title', event.target.value)} />
                </FormField>

                <FormField label="Hochgeladen von">
                  <input className="input" value={editForm.uploaded_by} onChange={(event) => setEditValue('uploaded_by', event.target.value)} />
                </FormField>

                <FormField label="Charge">
                  <select className="input" value={editForm.charge_id} onChange={(event) => setEditValue('charge_id', event.target.value)}>
                    <option value="">Nicht zugeordnet</option>
                    {charges.map((charge) => (
                      <option key={charge.id} value={charge.id}>
                        {charge.name}
                      </option>
                    ))}
                  </select>
                </FormField>

                <FormField label="Reaktor">
                  <select className="input" value={editForm.reactor_id} onChange={(event) => setEditValue('reactor_id', event.target.value)}>
                    <option value="">Nicht zugeordnet</option>
                    {reactors.map((reactor) => (
                      <option key={reactor.id} value={reactor.id}>
                        {reactor.name}
                      </option>
                    ))}
                  </select>
                </FormField>

                <FormField label="Aufgenommen am">
                  <input className="input" type="datetime-local" value={editForm.captured_at} onChange={(event) => setEditValue('captured_at', event.target.value)} />
                </FormField>
              </div>

              <FormField label="Notiz">
                <textarea className="input textarea" rows={6} value={editForm.notes} onChange={(event) => setEditValue('notes', event.target.value)} />
              </FormField>

              <div className="buttonRow">
                <button className="button" type="submit" disabled={saving}>
                  {saving ? 'Speichert…' : 'Metadaten speichern'}
                </button>
                <a className="button buttonSecondary" href={`${apiBase}${selectedPhoto.file_url}`} target="_blank" rel="noreferrer">
                  Datei oeffnen
                </a>
              </div>
            </form>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
