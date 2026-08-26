"""ACK and retry state model for Sahayak software testing."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .forwarding import ForwardPacket


@dataclass
class PendingTransmission:
    packet: ForwardPacket
    next_hop: int
    retry_count: int
    max_retries: int
    last_sent_ms: int


class ReliabilityManager:
    def __init__(self, max_pending: int = 8) -> None:
        self.max_pending = max_pending
        self.pending: list[PendingTransmission] = []

    def track(self, packet: ForwardPacket, next_hop: int, now_ms: int,
              max_retries: int = 3) -> bool:
        if len(self.pending) >= self.max_pending:
            return False
        self.pending.append(PendingTransmission(
            packet=packet,
            next_hop=next_hop,
            retry_count=0,
            max_retries=max_retries,
            last_sent_ms=now_ms,
        ))
        return True

    def acknowledge(self, origin_id: int, sequence: int) -> bool:
        for index, item in enumerate(self.pending):
            if (item.packet.origin_id == origin_id
                    and item.packet.sequence == sequence):
                self.pending.pop(index)
                return True
        return False

    def due_retry(self, now_ms: int, timeout_ms: int) -> PendingTransmission | None:
        for index, item in enumerate(self.pending):
            if now_ms - item.last_sent_ms < timeout_ms:
                continue
            if item.retry_count >= item.max_retries:
                continue
            updated = replace(item,
                               retry_count=item.retry_count + 1,
                               last_sent_ms=now_ms)
            self.pending[index] = updated
            return updated
        return None

    def expire_exhausted(self, now_ms: int,
                         timeout_ms: int) -> PendingTransmission | None:
        for index, item in enumerate(self.pending):
            if now_ms - item.last_sent_ms < timeout_ms:
                continue
            if item.retry_count < item.max_retries:
                continue
            return self.pending.pop(index)
        return None
