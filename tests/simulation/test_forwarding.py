from base_station.forwarding import (
    ForwardAction,
    ForwardPacket,
    Forwarder,
)


def packet(**overrides):
    values = dict(
        origin_id=5,
        sequence=1,
        sender_id=5,
        destination_id=1,
        previous_hop=255,
        ttl=3,
        hop_count=0,
        priority=3,
    )
    values.update(overrides)
    return ForwardPacket(**values)


def test_relay_queues_forwarded_packet_and_updates_path_metadata():
    forwarder = Forwarder(local_id=3)
    decision = forwarder.process(packet(), next_hop=1, now_ms=100)
    assert decision.action == ForwardAction.QUEUE
    assert decision.reason == "QUEUED"
    assert decision.packet is not None
    assert decision.packet.sender_id == 3
    assert decision.packet.previous_hop == 5
    assert decision.packet.ttl == 2
    assert decision.packet.hop_count == 1


def test_three_node_line_delivers_through_relay():
    relay = Forwarder(local_id=2)
    base = Forwarder(local_id=1)
    queued = relay.process(packet(), next_hop=1, now_ms=100)
    assert queued.packet is not None
    delivered = base.process(queued.packet, next_hop=None, now_ms=200)
    assert delivered.action == ForwardAction.DELIVER
    assert delivered.packet is not None
    assert delivered.packet.hop_count == 1


def test_destination_is_delivered():
    forwarder = Forwarder(local_id=1)
    decision = forwarder.process(packet(), next_hop=None, now_ms=100)
    assert decision.action == ForwardAction.DELIVER
    assert decision.reason == "DELIVERED"


def test_duplicate_is_dropped():
    forwarder = Forwarder(local_id=3)
    first = forwarder.process(packet(), next_hop=1, now_ms=100)
    second = forwarder.process(packet(), next_hop=1, now_ms=101)
    assert first.action == ForwardAction.QUEUE
    assert second.action == ForwardAction.DROP
    assert second.reason == "DUPLICATE"


def test_ttl_and_loop_protection():
    forwarder = Forwarder(local_id=3)
    expired = forwarder.process(packet(ttl=0, sequence=2), next_hop=1, now_ms=100)
    loop = forwarder.process(packet(sequence=3, previous_hop=1), next_hop=1,
                             now_ms=100)
    assert expired.reason == "TTL_EXPIRED"
    assert loop.reason == "ROUTE_LOOP"


def test_queue_overflow_is_explicit():
    forwarder = Forwarder(local_id=3, queue_size=1)
    first = forwarder.process(packet(sequence=10), next_hop=1, now_ms=100)
    second = forwarder.process(packet(sequence=11), next_hop=1, now_ms=100)
    assert first.reason == "QUEUED"
    assert second.reason == "QUEUE_FULL"


from base_station.reliability import ReliabilityManager


def test_ack_clears_pending_transmission():
    manager = ReliabilityManager()
    assert manager.track(packet(sequence=40), next_hop=2, now_ms=0)
    assert manager.acknowledge(origin_id=5, sequence=40)
    assert manager.pending == []


def test_retry_is_due_then_exhaustion_is_reported():
    manager = ReliabilityManager()
    assert manager.track(packet(sequence=41), next_hop=2, now_ms=0,
                         max_retries=1)
    retry = manager.due_retry(now_ms=2_500, timeout_ms=2_500)
    assert retry is not None
    assert retry.retry_count == 1
    exhausted = manager.expire_exhausted(now_ms=5_000, timeout_ms=2_500)
    assert exhausted is not None
    assert exhausted.retry_count == 1
    assert manager.pending == []


def test_pending_capacity_is_bounded():
    manager = ReliabilityManager(max_pending=1)
    assert manager.track(packet(sequence=50), next_hop=2, now_ms=0)
    assert not manager.track(packet(sequence=51), next_hop=2, now_ms=0)
