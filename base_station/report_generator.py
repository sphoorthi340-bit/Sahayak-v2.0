"""Generate a reproducible Markdown experiment summary from Sahayak events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping

from .data_quality import validate_events, validate_metadata
from .metrics import summarize_events
from .packet_parser import Event, parse_event


def load_events(path: str | Path) -> list[Event]:
    events: list[Event] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        event = parse_event(line)
        if event is not None:
            events.append(event)
    return events


def render_report(metadata: Mapping[str, object], events: Iterable[Event]) -> str:
    events = list(events)
    summary = summarize_events(events)
    metadata_issues = validate_metadata(metadata)
    event_issues = validate_events(events)
    source = str(metadata.get("source", "unknown"))
    quality = "PASS" if not any(
        issue.severity == "ERROR" for issue in [*metadata_issues, *event_issues]
    ) else "FAIL"

    def value(item: object | None) -> str:
        return "N/A" if item is None else str(item)

    lines = [
        f"# Sahayak Experiment Report: {metadata.get('experiment_id', 'unnamed')}",
        "",
        f"**Data source:** `{source}`  ",
        f"**Data-quality status:** `{quality}`  ",
        "",
        "> This report is generated from repository code. Simulation and synthetic "
        "results must not be described as hardware measurements.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Packets created/observed | {summary.created} |",
        f"| Packets delivered | {summary.delivered} |",
        f"| Packet delivery ratio | {summary.packet_delivery_ratio:.4f} |",
        f"| Mean latency (ms) | {value(summary.mean_latency_ms)} |",
        f"| Median latency (ms) | {value(summary.median_latency_ms)} |",
        f"| Total retries | {summary.total_retries} |",
        f"| Duplicate outcomes | {summary.duplicates} |",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(dict(metadata), indent=2, sort_keys=True),
        "```",
        "",
        "## Data-quality issues",
        "",
    ]
    issues = [*metadata_issues, *event_issues]
    if not issues:
        lines.append("No data-quality issues detected.")
    else:
        for issue in issues:
            lines.append(f"- **{issue.severity} `{issue.code}`:** {issue.message}")
    lines.extend(["", "## Interpretation boundary", "",
                  f"This report is labelled `{source}`. Replace synthetic or simulation "
                  "inputs with verified hardware logs before using any value as field evidence.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Sahayak Markdown report")
    parser.add_argument("events", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(metadata, load_events(args.events)),
                            encoding="utf-8")
    print(f"Wrote report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
