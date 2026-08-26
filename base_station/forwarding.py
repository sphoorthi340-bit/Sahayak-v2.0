"""Software forwarding primitives for the Sahayak three-node milestone."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, replace
from enum import Enum


class ForwardAction(str, Enum):
    DELIVER = "DELIVER"
    QUEUE = "QUEUE"
    DROP = "DROP"


@dataclass(frozen=True)
class ForwardPacket:
    origin_id: int
    sequence: int
    sender_id: int
    destination_id: int
    previous_hop: int
    ttl: int
    hop_count: int
    priority: int
    created_uptime_ms: int = 0

    @property
    def identity(self) -> tuple[int, int]:
        return self.origin_id, self.sequence


@dataclass(frozen=True)
class ForwardingDecision:
    action: ForwardAction
    reason: str
    packet: ForwardPacket | None = None


class DuplicateCache:
    def __init__(self, max_entries: int = 256, expiry_ms: int = 120_000) -> None:
        self.max_entries = max_entries
        self.expiry_ms = expiry_ms
        self._entries: OrderedDict[tuple[int, int], int] = OrderedDict()

    def contains(self, identity: tuple[int, int], now_ms: int) -> bool:
        self._expire(now_ms)
        return identity in self._entries

    def add(self, identity: tuple[int, int], now_ms: int) -> None:
        self._expire(now_ms)
        self._entries.pop(identity, None)
        self._entries[identity] = now_ms
        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)

    def _expire(self, now_ms: int) -> None:
        expired = [
            identity for identity, seen_ms in self._entries.items()
            if now_ms - seen_ms > self.expiry_ms
        ]
        for identity in expired:
            self._entries.pop(identity, None)


class BoundedPriorityQueue:
    def __init__(self, max_size: int = 16) -> None:
        self.max_size = max_size
        self._items: list[tuple[int, int, ForwardPacket]] = []
        self._counter = 0

    def enqueue(self, packet: ForwardPacket) -> bool:
        if len(self._items) >= self.max_size:
            return False
        # Higher priority first, FIFO within equal priority.
        self._items.append((-packet.priority, self._counter, packet))
        self._counter += 1
        self._items.sort(key=lambda item: (item[0], item[1]))
        return True

    def pop(self) -> ForwardPacket | None:
        if not self._items:
            return None
        return self._items.pop(0)[2]

    def __len__(self) -> int:
        return len(self._items)


class Forwarder:
    def __init__(self, local_id: int, queue_size: int = 16,
                 duplicate_cache_size: int = 256) -> None:
        self.local_id = local_id
        self.duplicates = DuplicateCache(max_entries=duplicate_cache_size)
        self.queue = BoundedPriorityQueue(max_size=queue_size)

    def process(self, packet: ForwardPacket, next_hop: int | None,
                now_ms: int) -> ForwardingDecision:
        if self.duplicates.contains(packet.identity, now_ms):
            return ForwardingDecision(ForwardAction.DROP, "DUPLICATE")
        self.duplicates.add(packet.identity, now_ms)

        if packet.ttl <= 0:
            return ForwardingDecision(ForwardAction.DROP, "TTL_EXPIRED")
        if packet.destination_id == self.local_id:
            return ForwardingDecision(ForwardAction.DELIVER, "DELIVERED", packet)
        if next_hop is None:
            return ForwardingDecision(ForwardAction.DROP, "NO_ROUTE")
        if next_hop == self.local_id or next_hop == packet.previous_hop:
            return ForwardingDecision(ForwardAction.DROP, "ROUTE_LOOP")

        forwarded = replace(
            packet,
            sender_id=self.local_id,
            previous_hop=packet.sender_id,
            ttl=packet.ttl - 1,
            hop_count=packet.hop_count + 1,
        )
        if not self.queue.enqueue(forwarded):
            return ForwardingDecision(ForwardAction.DROP, "QUEUE_FULL")
        return ForwardingDecision(ForwardAction.QUEUE, "QUEUED", forwarded)

    def next_queued_packet(self) -> ForwardPacket | None:
        return self.queue.pop()
