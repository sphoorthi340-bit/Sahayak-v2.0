"""Compact command semantics for future human-relay radio messages."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .human_relay import RelayAction


class CommandType(IntEnum):
    RELAY_DECISION = 1
    ROUTE_REFRESH = 2
    STATUS_REQUEST = 3


@dataclass(frozen=True)
class RelayCommand:
    origin_id: int
    sequence: int
    relay_id: int
    action: RelayAction
    issued_at_ms: int

    def encode(self) -> bytes:
        action_codes = {
            RelayAction.CORROBORATED: 1,
            RelayAction.REJECTED: 2,
            RelayAction.ESCALATED: 3,
        }
        if self.action not in action_codes:
            raise ValueError("Only final relay decisions can be encoded")
        return bytes([
            CommandType.RELAY_DECISION,
            self.origin_id & 0xFF,
            self.sequence & 0xFF,
            (self.sequence >> 8) & 0xFF,
            (self.sequence >> 16) & 0xFF,
            (self.sequence >> 24) & 0xFF,
            self.relay_id & 0xFF,
            action_codes[self.action],
            self.issued_at_ms & 0xFF,
            (self.issued_at_ms >> 8) & 0xFF,
            (self.issued_at_ms >> 16) & 0xFF,
            (self.issued_at_ms >> 24) & 0xFF,
        ])

    @classmethod
    def decode(cls, payload: bytes) -> "RelayCommand":
        if len(payload) != 12 or payload[0] != CommandType.RELAY_DECISION:
            raise ValueError("Invalid relay command payload")
        actions = {
            1: RelayAction.CORROBORATED,
            2: RelayAction.REJECTED,
            3: RelayAction.ESCALATED,
        }
        if payload[7] not in actions:
            raise ValueError("Unknown relay action code")
        sequence = int.from_bytes(payload[2:6], "little")
        issued_at_ms = int.from_bytes(payload[8:12], "little")
        return cls(payload[1], sequence, payload[6], actions[payload[7]], issued_at_ms)
