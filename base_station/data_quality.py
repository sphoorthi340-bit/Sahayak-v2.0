"""Validation rules for Sahayak event logs and experiment metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .packet_parser import Event


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    severity: str = "ERROR"


REQUIRED_HARDWARE_METADATA = {
    "experiment_id",
    "source",
    "firmware_commit",
    "node_ids",
    "radio_settings",
    "node_positions",
}


def validate_events(events: Iterable[Event]) -> list[QualityIssue]:
    events = list(events)
    issues: list[QualityIssue] = []
    if not events:
        return [QualityIssue("EMPTY_LOG", "No parseable EVENT records were found")]

    identities: set[tuple[int, int]] = set()
    for index, event in enumerate(events):
        if event.node is None:
            issues.append(QualityIssue("MISSING_NODE", f"Event {index} has no node ID"))
        if event.event_type == "REPORT" and event.sequence is None:
            issues.append(QualityIssue("MISSING_SEQUENCE",
                                       f"Report event {index} has no sequence"))
        if event.sequence is not None and event.origin is not None:
            identity = (event.origin, event.sequence)
            if event.event_type == "REPORT" and identity in identities:
                issues.append(QualityIssue(
                    "DUPLICATE_REPORT_ID",
                    f"Report identity {identity} appears more than once",
                    severity="WARNING",
                ))
            identities.add(identity)
    return issues


def validate_metadata(metadata: Mapping[str, object]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    missing = sorted(key for key in REQUIRED_HARDWARE_METADATA if not metadata.get(key))
    if missing:
        issues.append(QualityIssue(
            "MISSING_METADATA",
            "Missing required metadata: " + ", ".join(missing),
        ))
    source = str(metadata.get("source", "")).lower()
    if source not in {"synthetic", "simulation", "hardware"}:
        issues.append(QualityIssue(
            "INVALID_SOURCE",
            "source must be synthetic, simulation, or hardware",
        ))
    if source in {"synthetic", "simulation"} and metadata.get("hardware_claims"):
        issues.append(QualityIssue(
            "SIMULATION_HARDWARE_MIX",
            "Synthetic or simulation metadata cannot contain hardware claims",
        ))
    return issues


def can_support_hardware_claims(metadata: Mapping[str, object],
                                 events: Iterable[Event]) -> bool:
    source = str(metadata.get("source", "")).lower()
    return source == "hardware" and not any(
        issue.severity == "ERROR"
        for issue in [*validate_metadata(metadata), *validate_events(events)]
    )
