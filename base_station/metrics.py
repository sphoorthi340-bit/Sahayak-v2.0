"""Reusable metrics for Sahayak experiment results."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median
from typing import Iterable

from .packet_parser import Event


@dataclass(frozen=True)
class DeliverySummary:
    created: int
    delivered: int
    packet_delivery_ratio: float
    median_latency_ms: float | None
    mean_latency_ms: float | None
    total_retries: int
    duplicates: int


def _packet_key(event: Event) -> tuple[int | None, int | None]:
    return event.origin, event.sequence


def summarize_events(events: Iterable[Event]) -> DeliverySummary:
    events = list(events)
    created_keys = {
        _packet_key(event)
        for event in events
        if event.outcome in {"CREATED", "FORWARDED", "QUEUED"}
        and event.sequence is not None
    }
    delivered_keys = {
        _packet_key(event)
        for event in events
        if event.outcome == "DELIVERED" and event.sequence is not None
    }
    delivered = len(created_keys & delivered_keys) if created_keys else len(delivered_keys)
    created = len(created_keys) if created_keys else len({
        _packet_key(event) for event in events if event.sequence is not None
    })

    latencies: list[float] = []
    by_key: dict[tuple[int | None, int | None], list[Event]] = {}
    for event in events:
        by_key.setdefault(_packet_key(event), []).append(event)
    for packet_events in by_key.values():
        starts = [event.t_ms for event in packet_events if event.outcome == "CREATED"]
        ends = [event.t_ms for event in packet_events if event.outcome == "DELIVERED"]
        if starts and ends and starts[0] is not None and ends[-1] is not None:
            latency = ends[-1] - starts[0]
            if latency >= 0:
                latencies.append(float(latency))

    retries = sum(event.retry or 0 for event in events)
    duplicates = sum(1 for event in events if event.outcome == "DUPLICATE")
    pdr = delivered / created if created else 0.0

    return DeliverySummary(
        created=created,
        delivered=delivered,
        packet_delivery_ratio=pdr,
        median_latency_ms=median(latencies) if latencies else None,
        mean_latency_ms=mean(latencies) if latencies else None,
        total_retries=retries,
        duplicates=duplicates,
    )
