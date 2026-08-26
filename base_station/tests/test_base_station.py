from pathlib import Path

from base_station.logger import EventLogger
from base_station.packet_parser import parse_event


SAMPLE = (
    "EVENT,t_ms=12345,node=3,type=REPORT,origin=5,seq=1042,"
    "prev=5,next=1,hop=1,ttl=7,rssi=-94,snr=7.1,queue=0,retry=0,"
    "state=FORWARDED,outcome=QUEUED"
)


def test_parse_event():
    event = parse_event(SAMPLE)
    assert event is not None
    assert event.node == 3
    assert event.origin == 5
    assert event.sequence == 1042
    assert event.rssi == -94
    assert event.snr == 7.1
    assert event.outcome == "QUEUED"


def test_non_event_is_ignored():
    assert parse_event("Sahayak v2.0 firmware booting") is None


def test_missing_numeric_values_are_not_guessed():
    event = parse_event("EVENT,type=STATUS,node=2,snr=bad")
    assert event is not None
    assert event.node == 2
    assert event.snr is None
    assert event.sequence is None


def test_logger_persists_event(tmp_path: Path):
    database = tmp_path / "events.sqlite"
    logger = EventLogger(database)
    event = parse_event(SAMPLE)
    assert event is not None
    logger.log(event, scenario_id="smoke-001", firmware_version="0.1.0")
    assert logger.count() == 1
    logger.close()

    reopened = EventLogger(database)
    assert reopened.count() == 1
    reopened.close()
