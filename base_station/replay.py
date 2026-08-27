"""Replay Sahayak EVENT logs through the production parser and logger."""

from __future__ import annotations

import argparse
from pathlib import Path

from .logger import EventLogger
from .packet_parser import parse_event


def replay(input_path: str | Path, database_path: str | Path,
           scenario_id: str | None = None) -> int:
    logger = EventLogger(database_path)
    count = 0
    try:
        for line in Path(input_path).read_text(encoding="utf-8").splitlines():
            event = parse_event(line)
            if event is None:
                continue
            logger.log(event, scenario_id=scenario_id)
            count += 1
    finally:
        logger.close()
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay Sahayak EVENT telemetry")
    parser.add_argument("input", type=Path)
    parser.add_argument("--database", type=Path,
                        default=Path("experiments/processed_results/replay.sqlite"))
    parser.add_argument("--scenario-id", default="replay")
    args = parser.parse_args()
    count = replay(args.input, args.database, args.scenario_id)
    print(f"Replayed {count} events into {args.database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
