"""Vision analysis — FEATURE EXTRACTION + CLASSIFICATION ONLY.

Boundary Hardening V1: this module derives image features (color
statistics, sharpness, brightness, green/brown ratios) and produces a
`health_label` classification. That is all.

Explicitly NOT permitted:
- creating tasks, alerts, or commands from a classification,
- triggering schedules or reactor actions,
- auto-actions based on confidence thresholds.

Consumers (ABrain, operators, adapter) decide what to do with the
classification. `analyze_photo()` writes only the `VisionAnalysis` row
for the given photo — no side effects outside its own domain.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..config import settings
from ..models import Photo, VisionAnalysis
from ..schemas import VisionAnalysisRead


DOMINANT_BINS = 6


def analyze_image(photo_path: Path) -> dict[str, Any]:
    from PIL import Image, ImageFilter, ImageStat

    with Image.open(photo_path) as raw:
        raw.load()
        image = raw.convert('RGB')

    width, height = image.size
    stat = ImageStat.Stat(image)
    mean_r, mean_g, mean_b = stat.mean
    stddev_r, stddev_g, stddev_b = stat.stddev

    grayscale = image.convert('L')
    gray_stat = ImageStat.Stat(grayscale)
    brightness = round(gray_stat.mean[0] / 255.0, 4)

    sharpness_stat = ImageStat.Stat(grayscale.filter(ImageFilter.FIND_EDGES))
    sharpness = round(sharpness_stat.stddev[0] / 255.0, 4)

    downscaled = image.resize((48, 48))
    pixels = list(downscaled.getdata())
    histogram_bin_size = 256 // DOMINANT_BINS
    histogram: dict[tuple[int, int, int], int] = {}
    green_pixels = 0
    brown_pixels = 0

    for r, g, b in pixels:
        bucket = (
            r // histogram_bin_size,
            g // histogram_bin_size,
            b // histogram_bin_size,
        )
        histogram[bucket] = histogram.get(bucket, 0) + 1
        if g > r + 12 and g > b + 12:
            green_pixels += 1
        if r > 120 and g > 50 and b < 100 and r > b + 50 and abs(int(r) - int(g)) < 90:
            brown_pixels += 1

    dominant_bucket, dominant_count = max(histogram.items(), key=lambda item: item[1])
    dominant_rgb = [
        min(255, int(dominant_bucket[0] * histogram_bin_size + histogram_bin_size / 2)),
        min(255, int(dominant_bucket[1] * histogram_bin_size + histogram_bin_size / 2)),
        min(255, int(dominant_bucket[2] * histogram_bin_size + histogram_bin_size / 2)),
    ]
    dominant_ratio = round(dominant_count / len(pixels), 4)
    green_ratio = round(green_pixels / len(pixels), 4)
    brown_ratio = round(brown_pixels / len(pixels), 4)

    health_label = _classify_health(green_ratio, brown_ratio, brightness)
    confidence = round(_compute_confidence(green_ratio, brown_ratio, dominant_ratio, brightness, sharpness), 4)

    return {
        'width': width,
        'height': height,
        'avg_rgb': [round(mean_r, 2), round(mean_g, 2), round(mean_b, 2)],
        'rgb_stddev': [round(stddev_r, 2), round(stddev_g, 2), round(stddev_b, 2)],
        'brightness': brightness,
        'sharpness': sharpness,
        'dominant_rgb': dominant_rgb,
        'dominant_ratio': dominant_ratio,
        'green_ratio': green_ratio,
        'brown_ratio': brown_ratio,
        'health_label': health_label,
        'confidence': confidence,
    }


def analyze_photo(session: Session, photo: Photo, *, analysis_type: str = 'basic') -> VisionAnalysis:
    file_path = Path(settings.storage_path) / photo.storage_path
    if not file_path.is_file():
        analysis = VisionAnalysis(
            photo_id=photo.id,
            reactor_id=photo.reactor_id,
            analysis_type=analysis_type,
            status='failed',
            result={},
            error='stored photo file not found',
        )
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        return analysis

    try:
        result = analyze_image(file_path)
        analysis = VisionAnalysis(
            photo_id=photo.id,
            reactor_id=photo.reactor_id,
            analysis_type=analysis_type,
            status='ok',
            result=result,
            confidence=result.get('confidence'),
        )
    except Exception as exc:  # pragma: no cover - defensive
        analysis = VisionAnalysis(
            photo_id=photo.id,
            reactor_id=photo.reactor_id,
            analysis_type=analysis_type,
            status='failed',
            result={},
            error=str(exc)[:500],
        )

    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def list_analyses(session: Session, photo_id: int) -> list[VisionAnalysis]:
    return list(
        session.exec(
            select(VisionAnalysis)
            .where(VisionAnalysis.photo_id == photo_id)
            .order_by(VisionAnalysis.created_at.desc(), VisionAnalysis.id.desc())
        ).all()
    )


def get_latest_for_photos(session: Session, photo_ids: list[int]) -> dict[int, VisionAnalysis]:
    if not photo_ids:
        return {}
    analyses = session.exec(
        select(VisionAnalysis)
        .where(VisionAnalysis.photo_id.in_(photo_ids))
        .order_by(VisionAnalysis.photo_id.asc(), VisionAnalysis.created_at.desc(), VisionAnalysis.id.desc())
    ).all()
    latest: dict[int, VisionAnalysis] = {}
    for analysis in analyses:
        if analysis.photo_id not in latest:
            latest[analysis.photo_id] = analysis
    return latest


def get_latest_for_photo(session: Session, photo_id: int) -> VisionAnalysis | None:
    return get_latest_for_photos(session, [photo_id]).get(photo_id)


def get_latest_for_reactor(session: Session, reactor_id: int) -> VisionAnalysis | None:
    analyses = session.exec(
        select(VisionAnalysis)
        .where(VisionAnalysis.reactor_id == reactor_id)
        .where(VisionAnalysis.status == 'ok')
        .order_by(VisionAnalysis.created_at.desc(), VisionAnalysis.id.desc())
        .limit(1)
    ).all()
    return analyses[0] if analyses else None


def to_read(analysis: VisionAnalysis) -> VisionAnalysisRead:
    return VisionAnalysisRead(
        id=analysis.id,
        photo_id=analysis.photo_id,
        reactor_id=analysis.reactor_id,
        analysis_type=analysis.analysis_type,
        status=analysis.status,
        result=analysis.result,
        confidence=analysis.confidence,
        error=analysis.error,
        created_at=analysis.created_at,
    )


def get_analysis_or_404(session: Session, photo_id: int) -> VisionAnalysis:
    analysis = get_latest_for_photo(session, photo_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No vision analysis for photo yet')
    return analysis


def _classify_health(green_ratio: float, brown_ratio: float, brightness: float) -> str:
    if brightness < 0.08:
        return 'too_dark'
    if brightness > 0.94:
        return 'overexposed'
    if brown_ratio >= 0.25 and brown_ratio > green_ratio:
        return 'contamination_suspected'
    if green_ratio >= 0.45:
        return 'healthy_green'
    if green_ratio >= 0.2:
        return 'growing'
    if green_ratio >= 0.08:
        return 'low_biomass'
    return 'no_growth_visible'


def _compute_confidence(
    green_ratio: float,
    brown_ratio: float,
    dominant_ratio: float,
    brightness: float,
    sharpness: float,
) -> float:
    contrast_quality = 1.0 - abs(brightness - 0.5) * 2
    contrast_quality = max(0.0, min(1.0, contrast_quality))
    sharpness_quality = max(0.05, min(1.0, sharpness * 6))
    signal = max(green_ratio, brown_ratio, dominant_ratio)
    signal_quality = max(0.05, min(1.0, signal * 1.5))
    return max(0.0, min(1.0, (contrast_quality * 0.4) + (sharpness_quality * 0.3) + (signal_quality * 0.3)))
