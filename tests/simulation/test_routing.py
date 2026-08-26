from base_station.routing import RouteCandidate, RoutingWeights, select_next_hop


def test_adaptive_route_prefers_balanced_candidate():
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-100, hop_count=2, queue_length=0),
        RouteCandidate(next_hop=3, rssi_dbm=-90, hop_count=3, queue_length=8),
    ]
    selected = select_next_hop(candidates)
    assert selected is not None
    assert selected.next_hop in {2, 3}


def test_stale_and_unhealthy_routes_are_excluded():
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-70, hop_count=1, queue_length=0,
                       age_ms=40_000),
        RouteCandidate(next_hop=3, rssi_dbm=-100, hop_count=3, queue_length=2,
                       healthy=False),
    ]
    assert select_next_hop(candidates) is None


def test_weights_are_configurable():
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-75, hop_count=3, queue_length=5),
        RouteCandidate(next_hop=3, rssi_dbm=-100, hop_count=1, queue_length=0),
    ]
    hop_queue = RoutingWeights(rssi=0.1, hop=0.45, queue=0.45)
    selected = select_next_hop(candidates, weights=hop_queue)
    assert selected is not None
    assert selected.next_hop == 3


from base_station.routing import StableRouteSelector


def test_hysteresis_retains_current_route_for_small_improvement():
    selector = StableRouteSelector(hysteresis=0.10, current_next_hop=2)
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-90, hop_count=2, queue_length=1),
        RouteCandidate(next_hop=3, rssi_dbm=-89, hop_count=2, queue_length=1),
    ]
    selected = selector.select(candidates)
    assert selected is not None
    assert selected.next_hop == 2


def test_hysteresis_switches_for_meaningful_improvement():
    selector = StableRouteSelector(hysteresis=0.01, current_next_hop=2)
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-105, hop_count=3, queue_length=8),
        RouteCandidate(next_hop=3, rssi_dbm=-75, hop_count=1, queue_length=0),
    ]
    selected = selector.select(candidates)
    assert selected is not None
    assert selected.next_hop == 3


def test_hysteresis_switches_when_current_route_expires():
    selector = StableRouteSelector(hysteresis=0.10, current_next_hop=2)
    candidates = [
        RouteCandidate(next_hop=2, rssi_dbm=-80, hop_count=1, queue_length=0,
                       age_ms=31_000),
        RouteCandidate(next_hop=3, rssi_dbm=-95, hop_count=2, queue_length=2),
    ]
    selected = selector.select(candidates)
    assert selected is not None
    assert selected.next_hop == 3
