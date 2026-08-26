"""Run the software-only routing comparison for a Sahayak scenario."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .mesh_simulator import Link, MeshModel, SimulationConfig, Strategy, run_simulation
except ImportError:  # Supports direct execution from the repository root.
    from mesh_simulator import Link, MeshModel, SimulationConfig, Strategy, run_simulation


def load_scenario(path: Path) -> tuple[MeshModel, SimulationConfig]:
    data = json.loads(path.read_text(encoding="utf-8"))
    links = [Link(**item) for item in data["links"]]
    config = SimulationConfig(
        packet_count=int(data["packet_count"]),
        source=int(data["source"]),
        destination=int(data["destination"]),
        max_retries=int(data["max_retries"]),
        seed=int(data["seed"]),
        failure_nodes=set(data.get("failure_nodes", [])),
        max_hops=int(data.get("max_hops", 8)),
    )
    return MeshModel(links), config


def write_results(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "packet_id", "strategy", "delivered", "latency_ms", "hops",
        "retries", "selected_path", "failure_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sahayak routing comparison")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/processed_results/routing_comparison.csv"))
    args = parser.parse_args()

    model, config = load_scenario(args.scenario)
    rows: list[dict[str, object]] = []
    for strategy in Strategy:
        for result in run_simulation(model, strategy, config):
            rows.append({
                "packet_id": result.packet_id,
                "strategy": result.strategy,
                "delivered": int(result.delivered),
                "latency_ms": result.latency_ms,
                "hops": result.hops,
                "retries": result.retries,
                "selected_path": "-".join(map(str, result.selected_path)),
                "failure_reason": result.failure_reason or "",
            })

    write_results(args.output, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
