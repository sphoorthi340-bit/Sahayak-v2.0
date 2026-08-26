"""Run deterministic topology failure-risk scenarios for Sahayak."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from base_station.topology import (
    LinkObservation,
    build_graph,
    node_disjoint_path_count,
    risk_state,
)


def run(path: Path) -> list[dict[str, int | str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    base = int(data["base_station"])
    nodes = [int(node) for node in data["nodes"]]
    observations = [LinkObservation(**item) for item in data["links"]]
    rows: list[dict[str, int | str]] = []

    for failure_case in data["failure_cases"]:
        case_id = str(failure_case["case_id"])
        failed = {int(node) for node in failure_case.get("failed_nodes", [])}
        active = [
            observation for observation in observations
            if observation.source not in failed and observation.destination not in failed
        ]
        graph = build_graph(active, now_ms=1000, expiry_ms=30_000)
        for node in nodes:
            if node in failed:
                count = 0
                state = "FAILED"
            else:
                count = node_disjoint_path_count(graph, node, base=base)
                state = risk_state(count, desired_redundancy=2)
            rows.append({
                "case_id": case_id,
                "node": node,
                "failed_nodes": "-".join(map(str, sorted(failed))),
                "independent_paths": count,
                "state": state,
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sahayak failure-risk scenarios")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/processed_results/failure_risk.csv"))
    args = parser.parse_args()

    rows = run(args.scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case_id", "node", "failed_nodes", "independent_paths", "state"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
