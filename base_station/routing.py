"""Explainable route selection for the Sahayak adaptive-routing baseline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteCandidate:
    next_hop: int
    rssi_dbm: float
    hop_count: int
    queue_length: int
    healthy: bool = True
    age_ms: int = 0


@dataclass(frozen=True)
class RoutingWeights:
    rssi: float = 0.50
    hop: float = 0.25
    queue: float = 0.25


def _rssi_score(rssi_dbm: float) -> float:
    return max(0.0, min(1.0, (rssi_dbm + 120.0) / 55.0))


def _hop_score(hop_count: int) -> float:
    return 1.0 / max(1, hop_count)


def _queue_score(queue_length: int) -> float:
    return 1.0 / (1.0 + max(0, queue_length))


def route_score(candidate: RouteCandidate, weights: RoutingWeights) -> float:
    """Calculate a score where larger values are preferred."""
    if not candidate.healthy or candidate.age_ms < 0:
        return float("-inf")
    total = weights.rssi + weights.hop + weights.queue
    if total <= 0:
        raise ValueError("At least one routing weight must be positive")
    return (
        weights.rssi * _rssi_score(candidate.rssi_dbm)
        + weights.hop * _hop_score(candidate.hop_count)
        + weights.queue * _queue_score(candidate.queue_length)
    ) / total


def select_next_hop(candidates: list[RouteCandidate],
                   weights: RoutingWeights = RoutingWeights(),
                   max_age_ms: int = 30_000) -> RouteCandidate | None:
    """Select the best current candidate, or None when no route is valid."""
    valid = [
        candidate for candidate in candidates
        if candidate.healthy and candidate.age_ms <= max_age_ms
    ]
    if not valid:
        return None
    return max(
        valid,
        key=lambda candidate: (
            route_score(candidate, weights),
            -candidate.hop_count,
            -candidate.next_hop,
        ),
    )


@dataclass
class StableRouteSelector:
    """Retain a valid route unless a challenger exceeds the score margin."""

    hysteresis: float = 0.05
    current_next_hop: int | None = None

    def select(self, candidates: list[RouteCandidate],
               weights: RoutingWeights = RoutingWeights(),
               max_age_ms: int = 30_000) -> RouteCandidate | None:
        candidate = select_next_hop(candidates, weights, max_age_ms)
        current = next(
            (item for item in candidates
             if item.next_hop == self.current_next_hop
             and item.healthy and 0 <= item.age_ms <= max_age_ms),
            None,
        )

        if current is None:
            self.current_next_hop = candidate.next_hop if candidate else None
            return candidate
        if candidate is None or candidate.next_hop == current.next_hop:
            return current

        current_score = route_score(current, weights)
        candidate_score = route_score(candidate, weights)
        if candidate_score >= current_score + self.hysteresis:
            self.current_next_hop = candidate.next_hop
            return candidate
        return current
