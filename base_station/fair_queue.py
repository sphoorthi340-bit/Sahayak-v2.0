"""Priority queue with bounded aging for Sahayak triage experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueueItem:
    packet_id: int
    priority: int
    queued_at_ms: int


class FairPriorityQueue:
    def __init__(self, max_size: int = 32, aging_interval_ms: int = 5_000,
                 max_aging_boost: int = 2) -> None:
        self.max_size = max_size
        self.aging_interval_ms = aging_interval_ms
        self.max_aging_boost = max_aging_boost
        self._items: list[QueueItem] = []

    def enqueue(self, item: QueueItem) -> bool:
        if len(self._items) >= self.max_size:
            return False
        self._items.append(item)
        return True

    def pop(self, now_ms: int) -> QueueItem | None:
        if not self._items:
            return None

        def key(item: QueueItem) -> tuple[int, int, int]:
            age = max(0, now_ms - item.queued_at_ms)
            boost = min(self.max_aging_boost,
                        age // max(1, self.aging_interval_ms))
            return item.priority + boost, -item.queued_at_ms, -item.packet_id

        selected = max(self._items, key=key)
        self._items.remove(selected)
        return selected

    def __len__(self) -> int:
        return len(self._items)
