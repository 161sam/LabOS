'use client';

import { useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { LabelTarget } from '../lib/lab-resources';
import { Card } from './Card';
import { InlineMessage } from './InlineMessage';

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

function formatDateTime(value: string | null) {
  if (!value) {
    return 'Nicht gesetzt';
  }
  return new Date(value).toLocaleString('de-DE');
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unerwarteter Fehler';
}

export function ScanLabelView({ labelCode }: { labelCode: string }) {
  const [target, setTarget] = useState<LabelTarget | null>(null);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTarget() {
      setLoading(true);
      setPageError(null);
      try {
        setTarget(await apiRequest<LabelTarget>(`/api/v1/labels/${encodeURIComponent(labelCode)}/target`));
      } catch (error) {
        setTarget(null);
        setPageError(getErrorMessage(error));
      } finally {
        setLoading(false);
      }
    }

    void loadTarget();
  }, [labelCode]);

  if (loading) {
    return <InlineMessage>Lade Label-Ziel…</InlineMessage>;
  }

  if (!target) {
    return (
      <div className="grid" style={{ gap: 24 }}>
        <div>
          <h1>Scan / Label</h1>
          <p className="muted">Der Label-Code konnte nicht aufgeloest werden.</p>
        </div>
        {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}
        <Card title="Nicht gefunden">
          <p>Dieses Label ist unbekannt, inaktiv oder das Zielobjekt wurde entfernt.</p>
        </Card>
      </div>
    );
  }

  const { label } = target;
  const asset = target.asset;
  const inventoryItem = target.inventory_item;

  return (
    <div className="grid" style={{ gap: 24 }}>
      <div>
        <h1>Scan / Label</h1>
        <p className="muted">Browserfaehige Zielseite fuer reale Objekte im Lab. Damit bleiben Geraete und Materialien direkt adressierbar.</p>
      </div>

      {pageError ? <InlineMessage tone="error">{pageError}</InlineMessage> : null}

      <div className="grid cols-2">
        <Card title={`Label ${label.label_code}`}>
          <div className="stackBlock">
            <div className="buttonRow">
              <span className={`badge badge-${label.is_active ? 'available' : 'archived'}`}>
                {label.is_active ? 'aktiv' : 'inaktiv'}
              </span>
              <span className="badge badge-info">{label.target_type}</span>
            </div>

            <div className="detailList">
              <div className="detailRow"><span>Display-Name</span><strong>{label.display_name ?? label.target_name ?? 'Nicht gesetzt'}</strong></div>
              <div className="detailRow"><span>Zielobjekt</span><strong>{label.target_name ?? `#${label.target_id}`}</strong></div>
              <div className="detailRow"><span>Standort</span><strong>{label.location_snapshot ?? label.target_location ?? 'Nicht gesetzt'}</strong></div>
              <div className="detailRow"><span>Erstellt</span><strong>{formatDateTime(label.created_at)}</strong></div>
            </div>

            {label.note ? <p className="muted">{label.note}</p> : null}

            <div className="buttonRow">
              <a className="button buttonSecondary" href={label.target_manager_path}>
                Zielmodul oeffnen
              </a>
              <a className="button buttonSecondary" href="/labels">
                Labelverwaltung
              </a>
            </div>
          </div>
        </Card>

        <Card title="QR">
          <div className="qrPanel">
            <img className="qrPreview" src={`${apiBase}${label.qr_path}`} alt={`QR ${label.label_code}`} />
          </div>
          <div className="buttonRow">
            <a className="button buttonSecondary" href={`${apiBase}${label.qr_path}`} target="_blank" rel="noreferrer">
              QR oeffnen
            </a>
          </div>
        </Card>
      </div>

      {asset ? (
        <Card title="Asset-Ziel">
          <div className="detailList">
            <div className="detailRow"><span>Name</span><strong>{asset.name}</strong></div>
            <div className="detailRow"><span>Typ</span><strong>{asset.asset_type}</strong></div>
            <div className="detailRow"><span>Status</span><strong>{asset.status}</strong></div>
            <div className="detailRow"><span>Ort</span><strong>{[asset.location, asset.zone].filter(Boolean).join(' / ')}</strong></div>
            <div className="detailRow"><span>Hersteller / Modell</span><strong>{[asset.manufacturer, asset.model].filter(Boolean).join(' / ') || 'Nicht gesetzt'}</strong></div>
            <div className="detailRow"><span>Naechste Wartung</span><strong>{formatDateTime(asset.next_maintenance_at)}</strong></div>
          </div>
        </Card>
      ) : null}

      {inventoryItem ? (
        <Card title="Inventory-Ziel">
          <div className="detailList">
            <div className="detailRow"><span>Name</span><strong>{inventoryItem.name}</strong></div>
            <div className="detailRow"><span>Kategorie</span><strong>{inventoryItem.category}</strong></div>
            <div className="detailRow"><span>Status</span><strong>{inventoryItem.status}</strong></div>
            <div className="detailRow"><span>Bestand</span><strong>{inventoryItem.quantity} {inventoryItem.unit}</strong></div>
            <div className="detailRow"><span>Mindestbestand</span><strong>{inventoryItem.min_quantity === null ? 'Nicht gesetzt' : `${inventoryItem.min_quantity} ${inventoryItem.unit}`}</strong></div>
            <div className="detailRow"><span>Ort</span><strong>{[inventoryItem.location, inventoryItem.zone].filter(Boolean).join(' / ')}</strong></div>
            <div className="detailRow"><span>Asset-Zuordnung</span><strong>{inventoryItem.asset_name ?? 'Keine'}</strong></div>
          </div>
        </Card>
      ) : null}
    </div>
  );
}
