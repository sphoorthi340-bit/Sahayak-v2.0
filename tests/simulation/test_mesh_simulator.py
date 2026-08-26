import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from simulation.mesh_simulator import (  # noqa: E402
    Link,
    MeshModel,
    SimulationConfig,
    Strategy,
    choose_path,
    run_simulation,
)


def build_model() -> MeshModel:
    return MeshModel([
        Link(5, 3, -95, latency_ms=450, queue_length=1),
        Link(3, 1, -90, latency_ms=450, queue_length=4),
        Link(5, 2, -100, latency_ms=500, queue_length=0),
        Link(2, 1, -93, latency_ms=500, queue_length=0),
        Link(5, 4, -88, latency_ms=400, queue_length=7),
        Link(4, 1, -98, latency_ms=400, queue_length=0),
    ])


def test_all_strategies_find_a_path():
    model = build_model()
    for strategy in Strategy:
        path = choose_path(model, 5, 1, strategy, max_hops=8)
        assert path is not None
        assert path[0] == 5
        assert path[-1] == 1


def test_simulation_is_deterministic():
    model = build_model()
    config = SimulationConfig(packet_count=10, seed=7)
    first = run_simulation(model, Strategy.ADAPTIVE, config)
    second = run_simulation(model, Strategy.ADAPTIVE, config)
    assert first == second


def test_failed_relay_is_reported():
    model = build_model()
    config = SimulationConfig(packet_count=1, failure_nodes={3})
    result = run_simulation(model, Strategy.RSSI_ONLY, config)[0]
    assert result.delivered is False
    assert result.failure_reason in {"FAILED_NODE", "RETRY_LIMIT_REACHED"}
