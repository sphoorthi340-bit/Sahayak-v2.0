"""Parsing utilities for Sahayak serial telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Event:
    """A normalized firmware event.

    Unknown or missing fields are represented by None rather than guessed values.
    """

    raw: str
    t_ms: Optional[int] = None
    node: Optional[int] = None
    event_type: str = "UNKNOWN"
    origin: Optional[int] = None
    sequence: Optional[int] = None
    previous_hop: Optional[int] = None
    next_hop: Optional[int] = None
    hop: Optional[int] = None
    ttl: Optional[int] = None
    rssi: Optional[int] = None
    snr: Optional[float] = None
    queue: Optional[int] = None
    retry: Optional[int] = None
    state: Optional[str] = None
    outcome: Optional[str] = None
    fields: Dict[str, str] | None = None


def _int_or_none(value: str | None) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _float_or_none(value: str | None) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_event(line: str) -> Optional[Event]:
    """Parse one EVENT line. Non-EVENT lines return None."""
    raw = line.strip()
    if not raw or not raw.startswith("EVENT"):
        return None

    tokens = [token.strip() for token in raw.split(",")]
    if not tokens or tokens[0] != "EVENT":
        return None

    fields: Dict[str, str] = {}
    for token in tokens[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        fields[key.strip()] = value.strip()

    return Event(
        raw=raw,
        t_ms=_int_or_none(fields.get("t_ms")),
        node=_int_or_none(fields.get("node")),
        event_type=fields.get("type", "UNKNOWN"),
        origin=_int_or_none(fields.get("origin")),
        sequence=_int_or_none(fields.get("seq")),
        previous_hop=_int_or_none(fields.get("prev")),
        next_hop=_int_or_none(fields.get("next")),
        hop=_int_or_none(fields.get("hop")),
        ttl=_int_or_none(fields.get("ttl")),
        rssi=_int_or_none(fields.get("rssi")),
        snr=_float_or_none(fields.get("snr")),
        queue=_int_or_none(fields.get("queue")),
        retry=_int_or_none(fields.get("retry")),
        state=fields.get("state"),
        outcome=fields.get("outcome"),
        fields=fields,
    )
