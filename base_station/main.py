"""Sahayak base-station event receiver."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable, TextIO

from .logger import EventLogger
from .packet_parser import Event, parse_event


def lines_from_serial(port: str, baud: int) -> Iterable[str]:
    import serial  # Imported only when a real serial port is requested.

    with serial.Serial(port, baudrate=baud, timeout=1) as connection:
        while True:
            data = connection.readline()
            if data:
                yield data.decode("utf-8", errors="replace")


def lines_from_stdin(stream: TextIO) -> Iterable[str]:
    for line in stream:
        yield line


def run(lines: Iterable[str], logger: EventLogger,
        scenario_id: str | None = None) -> int:
    parsed_count = 0
    for line in lines:
        event = parse_event(line)
        if event is None:
            continue
        logger.log(event, scenario_id=scenario_id)
        parsed_count += 1
        print(
            f"[{event.t_ms if event.t_ms is not None else '-'} ms] "
            f"{event.event_type} origin={event.origin} seq={event.sequence} "
            f"outcome={event.outcome}"
        )
    return parsed_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sahayak base-station receiver")
    parser.add_argument("--serial-port", help="Serial device, e.g. /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument(
        "--database",
        default="experiments/raw_logs/sahayak.sqlite",
        help="SQLite database path",
    )
    parser.add_argument("--scenario-id", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logger = EventLogger(Path(args.database))
    try:
        if args.serial_port:
            count = run(
                lines_from_serial(args.serial_port, args.baud),
                logger,
                scenario_id=args.scenario_id,
            )
        else:
            count = run(lines_from_stdin(sys.stdin), logger,
                        scenario_id=args.scenario_id)
        print(f"Logged events: {count}")
    except KeyboardInterrupt:
        print("\nStopping receiver")
    finally:
        logger.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
