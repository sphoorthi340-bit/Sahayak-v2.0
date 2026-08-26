from pathlib import Path
import json

from base_station.forwarding import ForwardPacket
from base_station.human_relay import HumanRelayManager, RelayAction, RelayReport
from experiments.priority_surge import Arrival, simulate


def report(report_id=(5, 1), severity=2):
    return RelayReport(
        report_id=report_id,
        origin_id=5,
        severity=severity,
        confidence=4,
        people_affected=10,
        trapped_persons=1,
        region_id=2,
    )


def test_human_corrobation_escalates_priority():
    manager = HumanRelayManager()
    manager.ingest(report())
    updated = manager.decide((5, 1), relay_id=7,
                             action=RelayAction.CORROBORATED,
                             note="Visual confirmation")
    assert updated.effective_priority == 3
    assert updated.relay_id == 7
    assert manager.pending() == []


def test_rejected_report_is_deprioritized():
    manager = HumanRelayManager()
    manager.ingest(report(severity=3))
    updated = manager.decide((5, 1), relay_id=7,
                             action=RelayAction.REJECTED)
    assert updated.effective_priority <= 1


def test_priority_surge_serves_emergency_before_lower_priority_waiting_items():
    arrivals = [
        Arrival(packet_id=1, arrival_ms=0, priority=0, service_ms=100),
        Arrival(packet_id=2, arrival_ms=0, priority=1, service_ms=100),
        Arrival(packet_id=3, arrival_ms=50, priority=3, service_ms=100),
    ]
    served = simulate(arrivals, "priority")
    assert served[0].packet_id == 2
    assert served[1].packet_id == 3
    assert served[2].packet_id == 1


def test_priority_surge_is_deterministic():
    arrivals = [
        Arrival(packet_id=1, arrival_ms=0, priority=0, service_ms=100),
        Arrival(packet_id=2, arrival_ms=0, priority=1, service_ms=100),
    ]
    assert simulate(arrivals, "priority") == simulate(arrivals, "priority")


from base_station.recovery import (  # noqa: E402
    ConnectivitySnapshot,
    false_positive_warning,
    recovery_time,
    warning_time,
)


def test_recovery_metrics_measure_warning_and_recovery():
    snapshots = [
        ConnectivitySnapshot(0, 5, 2),
        ConnectivitySnapshot(1000, 5, 1),
        ConnectivitySnapshot(2500, 5, 2),
    ]
    assert warning_time(snapshots) == 1000
    assert recovery_time(snapshots) == 1500
    assert not false_positive_warning(snapshots, actual_failure_time_ms=900)


def test_missing_failure_ground_truth_is_flagged():
    snapshots = [ConnectivitySnapshot(1000, 5, 0)]
    assert false_positive_warning(snapshots, actual_failure_time_ms=None)


from base_station.fair_queue import FairPriorityQueue, QueueItem


def test_fair_queue_prefers_emergency_when_items_are_new():
    queue = FairPriorityQueue()
    queue.enqueue(QueueItem(packet_id=1, priority=0, queued_at_ms=0))
    queue.enqueue(QueueItem(packet_id=2, priority=3, queued_at_ms=0))
    assert queue.pop(now_ms=100).packet_id == 2


def test_fair_queue_aging_prevents_indefinite_starvation():
    queue = FairPriorityQueue(aging_interval_ms=100, max_aging_boost=2)
    queue.enqueue(QueueItem(packet_id=1, priority=0, queued_at_ms=0))
    queue.enqueue(QueueItem(packet_id=2, priority=1, queued_at_ms=900))
    assert queue.pop(now_ms=1000).packet_id == 1


def test_fair_queue_capacity_is_bounded():
    queue = FairPriorityQueue(max_size=1)
    assert queue.enqueue(QueueItem(packet_id=1, priority=1, queued_at_ms=0))
    assert not queue.enqueue(QueueItem(packet_id=2, priority=1, queued_at_ms=0))
