"""Reactor Health — CLASSIFICATION + SIGNAL EMISSION.

Boundary Hardening V1: `assess_reactor()` produces a *classification*
(`nominal` / `attention` / `warning` / `incident` / `unknown`) plus a
list of signals derived from telemetry, vision, and open safety
incidents. That is the full scope.

The classification is NOT a decision — it is a label describing the
current domain state. No task is created, no command is issued, no
schedule is adjusted from this module. Consumers (ABrain, operators)
decide what to do with the classification and signals.

If a future change feels like "when health is warning, do X" — stop.
That decision belongs on the other side of the adapter boundary.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import (
    Reactor,
    ReactorHealthAssessment,
    ReactorSetpoint,
    ReactorTwin,
    SafetyIncident,
    TelemetryValue,
    VisionAnalysis,
    _utcnow,
)
from ..schemas import (
    ReactorHealthAssessmentRead,
    ReactorHealthSignalRead,
    ReactorHealthSignalSeverity,
    ReactorHealthStatus,
)


STALE_TELEMETRY_HOURS = 6
VISION_LOW_GREEN_RATIO = 0.08
VISION_LOW_SHARPNESS = 0.05
VISION_LOW_CONFIDENCE = 0.3

_SEVERITY_ORDER = {
    ReactorHealthSignalSeverity.info: 0,
    ReactorHealthSignalSeverity.attention: 1,
    ReactorHealthSignalSeverity.warning: 2,
    ReactorHealthSignalSeverity.incident: 3,
}


def assess_reactor(session: Session, reactor_id: int) -> ReactorHealthAssessment:
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')

    twin = session.exec(select(ReactorTwin).where(ReactorTwin.reactor_id == reactor_id)).first()
    setpoints = list(session.exec(select(ReactorSetpoint).where(ReactorSetpoint.reactor_id == reactor_id)).all())
    telemetry_latest = _latest_telemetry_by_sensor(session, reactor_id)
    vision = _latest_vision(session, reactor_id)
    open_incidents = _open_incidents(session, reactor_id)

    signals: list[dict[str, Any]] = []
    signals.extend(_telemetry_signals(telemetry_latest, twin, setpoints))
    signals.extend(_vision_signals(vision))
    signals.extend(_safety_signals(open_incidents))

    status_value = _derive_status(signals, telemetry_latest, vision, open_incidents)
    summary = _build_summary(status_value, signals, reactor.name)

    source_telemetry_at = _latest_timestamp(telemetry_latest)
    source_vision_id = vision.id if vision is not None else None

    assessment = ReactorHealthAssessment(
        reactor_id=reactor_id,
        status=status_value.value,
        summary=summary,
        signals=signals,
        source_telemetry_at=source_telemetry_at,
        source_vision_analysis_id=source_vision_id,
        source_incident_count=len(open_incidents),
    )
    session.add(assessment)
    session.commit()
    session.refresh(assessment)
    return assessment


def list_latest_per_reactor(session: Session) -> list[ReactorHealthAssessment]:
    reactor_ids = [row for row in session.exec(select(Reactor.id)).all()]
    latest_map = get_latest_for_reactors(session, reactor_ids)
    return [latest_map[rid] for rid in sorted(latest_map.keys()) if latest_map.get(rid) is not None]


def get_latest_for_reactor(session: Session, reactor_id: int) -> ReactorHealthAssessment | None:
    return session.exec(
        select(ReactorHealthAssessment)
        .where(ReactorHealthAssessment.reactor_id == reactor_id)
        .order_by(ReactorHealthAssessment.assessed_at.desc(), ReactorHealthAssessment.id.desc())
        .limit(1)
    ).first()


def get_latest_for_reactors(session: Session, reactor_ids: list[int]) -> dict[int, ReactorHealthAssessment]:
    if not reactor_ids:
        return {}
    rows = list(
        session.exec(
            select(ReactorHealthAssessment)
            .where(ReactorHealthAssessment.reactor_id.in_(reactor_ids))
            .order_by(
                ReactorHealthAssessment.reactor_id.asc(),
                ReactorHealthAssessment.assessed_at.desc(),
                ReactorHealthAssessment.id.desc(),
            )
        ).all()
    )
    latest: dict[int, ReactorHealthAssessment] = {}
    for row in rows:
        if row.reactor_id not in latest:
            latest[row.reactor_id] = row
    return latest


def list_history_for_reactor(session: Session, reactor_id: int, *, limit: int = 20) -> list[ReactorHealthAssessment]:
    return list(
        session.exec(
            select(ReactorHealthAssessment)
            .where(ReactorHealthAssessment.reactor_id == reactor_id)
            .order_by(ReactorHealthAssessment.assessed_at.desc(), ReactorHealthAssessment.id.desc())
            .limit(limit)
        ).all()
    )


def to_read(assessment: ReactorHealthAssessment, *, reactor_name: str | None = None) -> ReactorHealthAssessmentRead:
    return ReactorHealthAssessmentRead(
        id=assessment.id,
        reactor_id=assessment.reactor_id,
        reactor_name=reactor_name,
        status=ReactorHealthStatus(assessment.status),
        summary=assessment.summary,
        signals=[ReactorHealthSignalRead(**signal) for signal in assessment.signals],
        source_telemetry_at=assessment.source_telemetry_at,
        source_vision_analysis_id=assessment.source_vision_analysis_id,
        source_incident_count=assessment.source_incident_count,
        assessed_at=assessment.assessed_at,
        created_at=assessment.created_at,
    )


def count_by_status(session: Session) -> dict[str, int]:
    """Return counts per status using the latest assessment per reactor.
    Reactors without any assessment count as 'unknown'."""
    reactor_ids = [row for row in session.exec(select(Reactor.id)).all()]
    latest_map = get_latest_for_reactors(session, reactor_ids)
    counts: dict[str, int] = {item.value: 0 for item in ReactorHealthStatus}
    for reactor_id in reactor_ids:
        assessment = latest_map.get(reactor_id)
        status_value = assessment.status if assessment is not None else ReactorHealthStatus.unknown.value
        counts[status_value] = counts.get(status_value, 0) + 1
    return counts


def _latest_telemetry_by_sensor(session: Session, reactor_id: int) -> dict[str, TelemetryValue]:
    rows = list(
        session.exec(
            select(TelemetryValue)
            .where(TelemetryValue.reactor_id == reactor_id)
            .order_by(TelemetryValue.timestamp.desc(), TelemetryValue.id.desc())
        ).all()
    )
    latest: dict[str, TelemetryValue] = {}
    for row in rows:
        latest.setdefault(row.sensor_type, row)
    return latest


def _latest_vision(session: Session, reactor_id: int) -> VisionAnalysis | None:
    return session.exec(
        select(VisionAnalysis)
        .where(VisionAnalysis.reactor_id == reactor_id)
        .where(VisionAnalysis.status == 'ok')
        .order_by(VisionAnalysis.created_at.desc(), VisionAnalysis.id.desc())
        .limit(1)
    ).first()


def _open_incidents(session: Session, reactor_id: int) -> list[SafetyIncident]:
    return list(
        session.exec(
            select(SafetyIncident)
            .where(SafetyIncident.reactor_id == reactor_id)
            .where(SafetyIncident.status != 'resolved')
        ).all()
    )


def _latest_timestamp(telemetry_latest: dict[str, TelemetryValue]) -> datetime | None:
    if not telemetry_latest:
        return None
    return max(value.timestamp for value in telemetry_latest.values())


def _twin_range(twin: ReactorTwin | None, parameter: str) -> tuple[float | None, float | None]:
    if twin is None:
        return None, None
    min_attr = f'target_{parameter}_min'
    max_attr = f'target_{parameter}_max'
    return getattr(twin, min_attr, None), getattr(twin, max_attr, None)


def _setpoint_range(setpoints: list[ReactorSetpoint], parameter: str) -> tuple[float | None, float | None]:
    for sp in setpoints:
        if sp.parameter == parameter:
            return sp.min_value, sp.max_value
    return None, None


def _resolve_range(
    twin: ReactorTwin | None,
    setpoints: list[ReactorSetpoint],
    parameter: str,
) -> tuple[float | None, float | None]:
    twin_min, twin_max = _twin_range(twin, parameter)
    if twin_min is not None or twin_max is not None:
        return twin_min, twin_max
    return _setpoint_range(setpoints, parameter)


_PARAMETER_LABELS = {
    'temp': 'Temperatur',
    'ph': 'pH',
    'light': 'Licht',
    'flow': 'Flow',
    'ec': 'EC',
    'co2': 'CO2',
    'humidity': 'Feuchte',
}


def _telemetry_signals(
    telemetry_latest: dict[str, TelemetryValue],
    twin: ReactorTwin | None,
    setpoints: list[ReactorSetpoint],
) -> list[dict[str, Any]]:
    if not telemetry_latest:
        return [
            {
                'code': 'telemetry_missing',
                'severity': ReactorHealthSignalSeverity.attention.value,
                'source': 'telemetry',
                'message': 'Keine Telemetriewerte fuer diesen Reaktor vorhanden.',
            }
        ]

    now = _utcnow()
    signals: list[dict[str, Any]] = []
    freshest = max(value.timestamp for value in telemetry_latest.values())
    stale = (now - freshest) > timedelta(hours=STALE_TELEMETRY_HOURS)
    if stale:
        signals.append(
            {
                'code': 'telemetry_stale',
                'severity': ReactorHealthSignalSeverity.attention.value,
                'source': 'telemetry',
                'message': f'Letzter Telemetriewert aelter als {STALE_TELEMETRY_HOURS} Stunden.',
            }
        )

    out_of_range_signals: list[dict[str, Any]] = []
    nominal_params: list[str] = []
    for sensor_type, value in telemetry_latest.items():
        min_v, max_v = _resolve_range(twin, setpoints, sensor_type)
        label = _PARAMETER_LABELS.get(sensor_type, sensor_type)
        if min_v is not None and value.value < min_v:
            out_of_range_signals.append(
                {
                    'code': f'telemetry_{sensor_type}_below_range',
                    'severity': ReactorHealthSignalSeverity.warning.value,
                    'source': 'telemetry',
                    'message': f'{label}-Wert {value.value} {value.unit} unter Zielbereich (min {min_v}).',
                }
            )
        elif max_v is not None and value.value > max_v:
            out_of_range_signals.append(
                {
                    'code': f'telemetry_{sensor_type}_above_range',
                    'severity': ReactorHealthSignalSeverity.warning.value,
                    'source': 'telemetry',
                    'message': f'{label}-Wert {value.value} {value.unit} ueber Zielbereich (max {max_v}).',
                }
            )
        elif min_v is not None or max_v is not None:
            nominal_params.append(label)

    signals.extend(out_of_range_signals)
    if not out_of_range_signals and not stale and nominal_params:
        signals.append(
            {
                'code': 'telemetry_nominal',
                'severity': ReactorHealthSignalSeverity.info.value,
                'source': 'telemetry',
                'message': 'Telemetrie innerhalb Zielbereich: ' + ', '.join(sorted(nominal_params)),
            }
        )
    return signals


def _vision_signals(vision: VisionAnalysis | None) -> list[dict[str, Any]]:
    if vision is None:
        return [
            {
                'code': 'vision_missing',
                'severity': ReactorHealthSignalSeverity.info.value,
                'source': 'vision',
                'message': 'Keine Vision-Analyse fuer diesen Reaktor vorhanden.',
            }
        ]

    result = vision.result or {}
    health_label = result.get('health_label')
    signals: list[dict[str, Any]] = []

    if health_label == 'contamination_suspected':
        signals.append(
            {
                'code': 'vision_contamination_suspected',
                'severity': ReactorHealthSignalSeverity.warning.value,
                'source': 'vision',
                'message': 'Vision-Analyse meldet Kontaminationsverdacht.',
            }
        )
    elif health_label == 'too_dark':
        signals.append(
            {
                'code': 'vision_low_brightness',
                'severity': ReactorHealthSignalSeverity.attention.value,
                'source': 'vision',
                'message': 'Bild zu dunkel fuer verlaessliche Auswertung.',
            }
        )
    elif health_label == 'overexposed':
        signals.append(
            {
                'code': 'vision_high_brightness',
                'severity': ReactorHealthSignalSeverity.attention.value,
                'source': 'vision',
                'message': 'Bild ueberbelichtet, Klassifikation unsicher.',
            }
        )
    elif health_label in ('no_growth_visible', 'low_biomass'):
        signals.append(
            {
                'code': 'vision_green_ratio_drop',
                'severity': ReactorHealthSignalSeverity.attention.value,
                'source': 'vision',
                'message': f'Vision-Klassifikation: {health_label} (wenig gruene Biomasse sichtbar).',
            }
        )
    elif health_label in ('healthy_green', 'growing'):
        signals.append(
            {
                'code': 'vision_nominal',
                'severity': ReactorHealthSignalSeverity.info.value,
                'source': 'vision',
                'message': f'Vision-Klassifikation: {health_label}.',
            }
        )

    green_ratio = result.get('green_ratio')
    if isinstance(green_ratio, (int, float)) and green_ratio < VISION_LOW_GREEN_RATIO and health_label not in ('contamination_suspected',):
        if not any(signal['code'] == 'vision_green_ratio_drop' for signal in signals):
            signals.append(
                {
                    'code': 'vision_green_ratio_drop',
                    'severity': ReactorHealthSignalSeverity.attention.value,
                    'source': 'vision',
                    'message': f'Gruenanteil {green_ratio:.2f} unter Schwellwert {VISION_LOW_GREEN_RATIO}.',
                }
            )

    sharpness = result.get('sharpness')
    if isinstance(sharpness, (int, float)) and sharpness < VISION_LOW_SHARPNESS:
        signals.append(
            {
                'code': 'vision_low_sharpness',
                'severity': ReactorHealthSignalSeverity.info.value,
                'source': 'vision',
                'message': f'Bildschaerfe {sharpness:.3f} niedrig – Aussage mit Vorbehalt.',
            }
        )

    if vision.confidence is not None and vision.confidence < VISION_LOW_CONFIDENCE:
        signals.append(
            {
                'code': 'vision_low_confidence',
                'severity': ReactorHealthSignalSeverity.info.value,
                'source': 'vision',
                'message': f'Vision-Konfidenz {vision.confidence:.2f} niedrig.',
            }
        )

    return signals


def _safety_signals(incidents: list[SafetyIncident]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for incident in incidents:
        if incident.severity == 'critical':
            severity = ReactorHealthSignalSeverity.incident.value
            code = 'safety_critical_incident_open'
        elif incident.severity == 'high':
            severity = ReactorHealthSignalSeverity.warning.value
            code = 'safety_high_incident_open'
        elif incident.severity == 'warning':
            severity = ReactorHealthSignalSeverity.attention.value
            code = 'safety_incident_open'
        else:
            severity = ReactorHealthSignalSeverity.info.value
            code = 'safety_incident_info'
        signals.append(
            {
                'code': code,
                'severity': severity,
                'source': 'safety',
                'message': f'Offener Incident #{incident.id}: {incident.title}',
            }
        )
    return signals


def _derive_status(
    signals: list[dict[str, Any]],
    telemetry_latest: dict[str, TelemetryValue],
    vision: VisionAnalysis | None,
    open_incidents: list[SafetyIncident],
) -> ReactorHealthStatus:
    severities = {signal['severity'] for signal in signals}

    if not telemetry_latest and vision is None and not open_incidents:
        return ReactorHealthStatus.unknown
    if ReactorHealthSignalSeverity.incident.value in severities:
        return ReactorHealthStatus.incident
    if ReactorHealthSignalSeverity.warning.value in severities:
        return ReactorHealthStatus.warning
    if ReactorHealthSignalSeverity.attention.value in severities:
        return ReactorHealthStatus.attention
    return ReactorHealthStatus.nominal


def _build_summary(
    status_value: ReactorHealthStatus,
    signals: list[dict[str, Any]],
    reactor_name: str,
) -> str:
    if status_value == ReactorHealthStatus.unknown:
        return f'Keine verwertbaren Daten fuer {reactor_name}.'
    sorted_signals = sorted(
        signals,
        key=lambda signal: _SEVERITY_ORDER.get(ReactorHealthSignalSeverity(signal['severity']), 0),
        reverse=True,
    )
    highlighted = [signal['message'] for signal in sorted_signals[:3]]
    header_map = {
        ReactorHealthStatus.nominal: f'{reactor_name} laeuft nominal.',
        ReactorHealthStatus.attention: f'{reactor_name} zeigt Auffaelligkeiten.',
        ReactorHealthStatus.warning: f'{reactor_name} hat Warnsignale.',
        ReactorHealthStatus.incident: f'{reactor_name} hat einen offenen Incident.',
    }
    header = header_map[status_value]
    if not highlighted:
        return header
    return header + ' ' + ' '.join(highlighted)
