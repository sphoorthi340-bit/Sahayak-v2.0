"""Topology and path-redundancy helpers for Sahayak."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx


@dataclass(frozen=True)
class LinkObservation:
    source: int
    destination: int
    last_heard_ms: int
    rssi: float | None = None
    snr: float | None = None
    healthy: bool = True


def build_graph(
    links: Iterable[LinkObservation],
    now_ms: int,
    expiry_ms: int = 30_000,
) -> nx.Graph:
    """Build an undirected graph from recent healthy link observations."""
    graph = nx.Graph()
    for link in links:
        if not link.healthy:
            continue
        if now_ms - link.last_heard_ms > expiry_ms:
            continue
        graph.add_edge(
            link.source,
            link.destination,
            rssi=link.rssi,
            snr=link.snr,
            last_heard_ms=link.last_heard_ms,
        )
    return graph


def node_disjoint_path_count(graph: nx.Graph, node: int, base: int = 1) -> int:
    """Return the number of internally node-disjoint paths to the base."""
    if node == base:
        return 1
    if node not in graph or base not in graph:
        return 0
    try:
        paths = nx.node_disjoint_paths(graph, node, base)
        return sum(1 for _ in paths)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return 0


def risk_state(path_count: int, desired_redundancy: int = 2) -> str:
    """Map independent path count to a conservative node state."""
    if path_count <= 0:
        return "ISOLATED"
    if path_count < desired_redundancy:
        return "AT_RISK"
    return "CONNECTED"


def risk_report(graph: nx.Graph, nodes: Iterable[int], base: int = 1,
                desired_redundancy: int = 2) -> list[dict[str, int | str]]:
    """Generate a compact risk report for the requested nodes."""
    report: list[dict[str, int | str]] = []
    for node in sorted(set(nodes)):
        count = node_disjoint_path_count(graph, node, base=base)
        report.append(
            {
                "node": node,
                "independent_paths": count,
                "state": risk_state(count, desired_redundancy),
            }
        )
    return report
