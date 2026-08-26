"""Human-relay decision layer for Sahayak emergency reports.

This is intentionally rule-based and auditable. It provides a protocol-level
place for a human relay to corroborate or reject reports without pretending
that a UI alone is a networking contribution.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class RelayAction(str, Enum):
    PENDING = "PENDING"
    CORROBORATED = "CORROBORATED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass(frozen=True)
class RelayReport:
    report_id: tuple[int, int]
    origin_id: int
    severity: int
    confidence: int
    people_affected: int
    trapped_persons: int
    region_id: int
    action: RelayAction = RelayAction.PENDING
    relay_id: int | None = None
    operator_note: str = ""

    @property
    def effective_priority(self) -> int:
        if self.action in {RelayAction.CORROBORATED, RelayAction.ESCALATED}:
            return 3
        if self.action == RelayAction.REJECTED:
            return max(0, min(1, self.severity - 2))
        return max(0, min(3, self.severity))


class HumanRelayManager:
    def __init__(self) -> None:
        self._reports: dict[tuple[int, int], RelayReport] = {}

    def ingest(self, report: RelayReport) -> RelayReport:
        existing = self._reports.get(report.report_id)
        if existing is not None:
            return existing
        self._reports[report.report_id] = report
        return report

    def decide(self, report_id: tuple[int, int], relay_id: int,
               action: RelayAction, note: str = "") -> RelayReport:
        if report_id not in self._reports:
            raise KeyError(f"Unknown report {report_id}")
        if action == RelayAction.PENDING:
            raise ValueError("A relay decision must change the report state")
        updated = replace(self._reports[report_id], action=action,
                          relay_id=relay_id, operator_note=note)
        self._reports[report_id] = updated
        return updated

    def get(self, report_id: tuple[int, int]) -> RelayReport | None:
        return self._reports.get(report_id)

    def priority_order(self) -> list[RelayReport]:
        return sorted(
            self._reports.values(),
            key=lambda report: (
                -report.effective_priority,
                -report.trapped_persons,
                -report.people_affected,
                report.report_id,
            ),
        )

    def pending(self) -> list[RelayReport]:
        return [report for report in self.priority_order()
                if report.action == RelayAction.PENDING]
