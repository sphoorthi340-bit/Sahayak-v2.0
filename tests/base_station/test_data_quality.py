from base_station.data_quality import (
    can_support_hardware_claims,
    validate_events,
    validate_metadata,
)
from base_station.packet_parser import parse_event


def event(line):
    parsed = parse_event(line)
    assert parsed is not None
    return parsed


def test_empty_log_is_invalid():
    issues = validate_events([])
    assert issues[0].code == "EMPTY_LOG"


def test_missing_hardware_metadata_is_reported():
    issues = validate_metadata({"source": "hardware"})
    assert any(issue.code == "MISSING_METADATA" for issue in issues)


def test_simulation_cannot_claim_hardware_results():
    issues = validate_metadata({
        "experiment_id": "sim-1",
        "source": "simulation",
        "firmware_commit": "abc123",
        "node_ids": [1, 2],
        "radio_settings": {"frequency": 866500000},
        "node_positions": {"1": [0, 0], "2": [1, 0]},
        "hardware_claims": True,
    })
    assert any(issue.code == "SIMULATION_HARDWARE_MIX" for issue in issues)


def test_complete_hardware_metadata_and_events_are_eligible():
    metadata = {
        "experiment_id": "hw-1",
        "source": "hardware",
        "firmware_commit": "abc123",
        "node_ids": [1, 2],
        "radio_settings": {"frequency": 866500000},
        "node_positions": {"1": [0, 0], "2": [1, 0]},
    }
    events = [event(
        "EVENT,t_ms=1,node=1,type=REPORT,origin=2,seq=1,prev=2,next=1,"
        "hop=1,ttl=7,rssi=-80,snr=8.0,queue=0,retry=0,state=CONNECTED,"
        "outcome=DELIVERED"
    )]
    assert can_support_hardware_claims(metadata, events)
