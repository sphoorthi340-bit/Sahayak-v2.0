"""Explainable emergency-report priority scoring for Sahayak."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmergencyReport:
    severity: int
    people_affected: int
    trapped_persons: int
    confidence: int
    age_seconds: float
    region_weight: float = 1.0
    human_confirmed: bool = False


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def priority_score(report: EmergencyReport) -> float:
    """Return a transparent score; higher values are more urgent."""
    severity = _clamp(report.severity, 0, 5) / 5.0
    affected = _clamp(report.people_affected, 0, 100) / 100.0
    trapped = _clamp(report.trapped_persons, 0, 20) / 20.0
    confidence = _clamp(report.confidence, 0, 5) / 5.0
    freshness = 1.0 / (1.0 + max(0.0, report.age_seconds) / 60.0)
    corroboration = 0.10 if report.human_confirmed else 0.0

    raw = (
        0.35 * severity
        + 0.20 * affected
        + 0.25 * trapped
        + 0.10 * confidence
        + 0.10 * freshness
        + corroboration
    )
    return raw * max(0.1, report.region_weight)


def priority_label(score: float) -> str:
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.50:
        return "HIGH"
    if score >= 0.25:
        return "MEDIUM"
    return "LOW"
