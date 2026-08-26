import networkx as nx

from base_station.priority_engine import EmergencyReport, priority_label, priority_score
from base_station.topology import node_disjoint_path_count, risk_state


def test_node_disjoint_paths():
    graph = nx.Graph()
    graph.add_edges_from([(5, 3), (5, 2), (3, 1), (2, 1)])
    assert node_disjoint_path_count(graph, 5, base=1) == 2


def test_shared_relay_is_not_two_independent_paths():
    graph = nx.Graph()
    graph.add_edges_from([(5, 3), (4, 3), (3, 1)])
    assert node_disjoint_path_count(graph, 5, base=1) == 1


def test_risk_state():
    assert risk_state(0) == "ISOLATED"
    assert risk_state(1) == "AT_RISK"
    assert risk_state(2) == "CONNECTED"


def test_priority_score_is_explainable_and_ordered():
    critical = EmergencyReport(
        severity=5,
        people_affected=80,
        trapped_persons=5,
        confidence=5,
        age_seconds=2,
        human_confirmed=True,
    )
    routine = EmergencyReport(
        severity=1,
        people_affected=1,
        trapped_persons=0,
        confidence=2,
        age_seconds=300,
    )
    assert priority_score(critical) > priority_score(routine)
    assert priority_label(priority_score(critical)) in {"HIGH", "CRITICAL"}
