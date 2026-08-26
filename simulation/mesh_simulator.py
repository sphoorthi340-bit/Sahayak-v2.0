"""Software-only Sahayak mesh simulation.

This simulator is a logic-development tool, not a replacement for field data.
It lets the team test route selection, bounded retries, failures, and metrics
before hardware is available.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

import networkx as nx


class Strategy(str, Enum):
    FLOOD = "flood"
    RSSI_ONLY = "rssi_only"
    ADAPTIVE = "adaptive"


@dataclass(frozen=True)
class Link:
    source: int
    destination: int
    rssi_dbm: float
    latency_ms: int = 500
    queue_length: int = 0

    @property
    def reliability(self) -> float:
        """A conservative deterministic mapping from RSSI to link success.

        This is only a tunable simulation assumption. It must never be reported
        as measured radio behavior.
        """
        normalized = (self.rssi_dbm + 120.0) / 55.0
        return max(0.10, min(0.99, normalized))


@dataclass
class SimulationConfig:
    packet_count: int = 100
    source: int = 5
    destination: int = 1
    max_retries: int = 2
    seed: int = 42
    failure_nodes: set[int] = field(default_factory=set)
    max_hops: int = 8


@dataclass
class PacketResult:
    packet_id: int
    strategy: str
    delivered: bool
    latency_ms: int
    hops: int
    retries: int
    selected_path: tuple[int, ...]
    failure_reason: str | None = None


class MeshModel:
    def __init__(self, links: Iterable[Link]) -> None:
        self.links = list(links)
        self.graph = nx.Graph()
        for link in self.links:
            self.graph.add_edge(
                link.source,
                link.destination,
                rssi_dbm=link.rssi_dbm,
                latency_ms=link.latency_ms,
                queue_length=link.queue_length,
            )

    def link(self, source: int, destination: int) -> Link:
        for link in self.links:
            if {link.source, link.destination} == {source, destination}:
                return link
        raise KeyError(f"No link between {source} and {destination}")

    def candidate_paths(self, source: int, destination: int,
                        max_hops: int) -> list[tuple[int, ...]]:
        if source not in self.graph or destination not in self.graph:
            return []
        paths = nx.all_simple_paths(self.graph, source, destination,
                                    cutoff=max_hops)
        return [tuple(path) for path in paths]

    def path_links(self, path: tuple[int, ...]) -> list[Link]:
        return [self.link(left, right) for left, right in zip(path, path[1:])]

    def path_metrics(self, path: tuple[int, ...]) -> dict[str, float]:
        links = self.path_links(path)
        if not links:
            return {"rssi": 0.0, "hop": 0.0, "queue": 0.0}
        rssi_scores = [max(0.0, min(1.0, (link.rssi_dbm + 120.0) / 55.0))
                       for link in links]
        queue_scores = [1.0 / (1.0 + max(0, link.queue_length))
                        for link in links]
        return {
            "rssi": sum(rssi_scores) / len(rssi_scores),
            "hop": 1.0 / len(links),
            "queue": sum(queue_scores) / len(queue_scores),
        }


def choose_path(model: MeshModel, source: int, destination: int,
                strategy: Strategy, max_hops: int) -> tuple[int, ...] | None:
    paths = model.candidate_paths(source, destination, max_hops)
    if not paths:
        return None

    if strategy == Strategy.FLOOD:
        # The simulator represents bounded flooding by selecting the shortest
        # candidate for latency accounting while permitting fallback paths in
        # the run loop. It is not a complete MAC-layer flood implementation.
        return min(paths, key=lambda path: (len(path), path))

    if strategy == Strategy.RSSI_ONLY:
        return max(
            paths,
            key=lambda path: (
                model.path_metrics(path)["rssi"],
                -len(path),
                tuple(-node for node in path),
            ),
        )

    return max(
        paths,
        key=lambda path: (
            0.50 * model.path_metrics(path)["rssi"]
            + 0.25 * model.path_metrics(path)["hop"]
            + 0.25 * model.path_metrics(path)["queue"],
            -len(path),
            tuple(-node for node in path),
        ),
    )


def _path_available(path: tuple[int, ...], failure_nodes: set[int]) -> bool:
    return not any(node in failure_nodes for node in path[1:-1])


def _attempt_path(model: MeshModel, path: tuple[int, ...], packet_id: int,
                  strategy: Strategy, config: SimulationConfig) -> PacketResult:
    if not path:
        return PacketResult(packet_id, strategy.value, False, 0, 0, 0, (),
                            "NO_ROUTE")
    if len(path) - 1 > config.max_hops:
        return PacketResult(packet_id, strategy.value, False, 0, len(path) - 1,
                            0, path, "TTL_EXPIRED")
    if not _path_available(path, config.failure_nodes):
        return PacketResult(packet_id, strategy.value, False, 0, len(path) - 1,
                            0, path, "FAILED_NODE")

    latency = 0
    retries = 0
    rng = random.Random(config.seed + packet_id)
    for link in model.path_links(path):
        delivered = False
        for attempt in range(config.max_retries + 1):
            latency += link.latency_ms
            if rng.random() <= link.reliability:
                delivered = True
                retries += attempt
                break
            retries += 1
        if not delivered:
            return PacketResult(packet_id, strategy.value, False, latency,
                                len(path) - 1, retries, path,
                                "RETRY_LIMIT_REACHED")

    return PacketResult(packet_id, strategy.value, True, latency,
                        len(path) - 1, retries, path)


def run_simulation(model: MeshModel, strategy: Strategy,
                   config: SimulationConfig) -> list[PacketResult]:
    results: list[PacketResult] = []
    for packet_id in range(1, config.packet_count + 1):
        path = choose_path(model, config.source, config.destination,
                           strategy, config.max_hops)
        results.append(_attempt_path(model, path or (), packet_id, strategy,
                                     config))
    return results
