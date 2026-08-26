"""Connectivity-risk and recovery measurements for Sahayak experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectivitySnapshot:
    time_ms: int
    node_id: int
    independent_paths: int

    @property
    def healthy(self) -> bool:
        return self.independent_paths >= 2

    @property
    def at_risk(self) -> bool:
        return self.independent_paths == 1

    @property
    def isolated(self) -> bool:
        return self.independent_paths == 0


def warning_time(snapshots: list[ConnectivitySnapshot]) -> int | None:
    """Return the first time a node becomes at risk or isolated."""
    for snapshot in sorted(snapshots, key=lambda item: item.time_ms):
        if snapshot.at_risk or snapshot.isolated:
            return snapshot.time_ms
    return None


def recovery_time(snapshots: list[ConnectivitySnapshot],
                  desired_paths: int = 2) -> int | None:
    """Return elapsed time from first warning until desired redundancy returns."""
    ordered = sorted(snapshots, key=lambda item: item.time_ms)
    warning = next((item for item in ordered if item.independent_paths < desired_paths),
                   None)
    if warning is None:
        return 0
    recovered = next((item for item in ordered
                      if item.time_ms >= warning.time_ms
                      and item.independent_paths >= desired_paths), None)
    if recovered is None:
        return None
    return recovered.time_ms - warning.time_ms


def false_positive_warning(snapshots: list[ConnectivitySnapshot],
                           actual_failure_time_ms: int | None) -> bool:
    """Mark a warning that occurred without a supplied actual failure event."""
    first_warning = warning_time(snapshots)
    return first_warning is not None and actual_failure_time_ms is None
