"""Deterministic queue experiment for Sahayak report triage."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Arrival:
    packet_id: int
    arrival_ms: int
    priority: int
    service_ms: int


@dataclass(frozen=True)
class Served:
    packet_id: int
    priority: int
    arrival_ms: int
    service_start_ms: int
    service_end_ms: int
    waiting_ms: int


def simulate(arrivals: list[Arrival], mode: str) -> list[Served]:
    pending = list(arrivals)
    served: list[Served] = []
    now_ms = 0
    while pending:
        available = [item for item in pending if item.arrival_ms <= now_ms]
        if not available:
            now_ms = min(item.arrival_ms for item in pending)
            available = [item for item in pending if item.arrival_ms <= now_ms]
        if mode == "priority":
            selected = max(available, key=lambda item: (item.priority, -item.packet_id))
        elif mode == "fifo":
            selected = min(available, key=lambda item: (item.arrival_ms, item.packet_id))
        else:
            raise ValueError(f"Unknown mode: {mode}")
        pending.remove(selected)
        start = max(now_ms, selected.arrival_ms)
        end = start + selected.service_ms
        served.append(Served(
            packet_id=selected.packet_id,
            priority=selected.priority,
            arrival_ms=selected.arrival_ms,
            service_start_ms=start,
            service_end_ms=end,
            waiting_ms=start - selected.arrival_ms,
        ))
        now_ms = end
    return served


def load(path: Path) -> list[Arrival]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Arrival(**item) for item in data["arrivals"]]


def write(path: Path, rows: list[dict[str, int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sahayak priority-surge experiment")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/processed_results/priority_surge.csv"))
    args = parser.parse_args()

    arrivals = load(args.scenario)
    rows: list[dict[str, int | str]] = []
    for mode in ("fifo", "priority"):
        for item in simulate(arrivals, mode):
            rows.append({
                "mode": mode,
                "packet_id": item.packet_id,
                "priority": item.priority,
                "arrival_ms": item.arrival_ms,
                "service_start_ms": item.service_start_ms,
                "service_end_ms": item.service_end_ms,
                "waiting_ms": item.waiting_ms,
            })
    write(args.output, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
