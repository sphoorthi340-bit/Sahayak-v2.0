import json
from pathlib import Path

from base_station.report_generator import load_events, render_report


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_pair.log"


def test_report_generator_labels_synthetic_data_and_metrics():
    metadata = {
        "experiment_id": "synthetic-pair",
        "source": "synthetic",
        "firmware_commit": "local",
        "node_ids": [1, 2],
        "radio_settings": {"frequency": 866500000},
        "node_positions": {"1": [0, 0], "2": [1, 0]},
    }
    report = render_report(metadata, load_events(FIXTURE))
    assert "Data source:** `synthetic`" in report
    assert "Packet delivery ratio" in report
    assert "Replace synthetic or simulation inputs" in report


def test_report_generator_marks_missing_metadata():
    report = render_report({"experiment_id": "bad", "source": "hardware"}, [])
    assert "Data-quality status:** `FAIL`" in report
    assert "MISSING_METADATA" in report


from base_station.commands import RelayCommand
from base_station.human_relay import RelayAction


def test_relay_command_round_trip():
    command = RelayCommand(5, 0x01020304, 7, RelayAction.ESCALATED, 123456)
    decoded = RelayCommand.decode(command.encode())
    assert decoded == command


def test_pending_relay_command_cannot_be_encoded():
    command = RelayCommand(5, 1, 7, RelayAction.PENDING, 100)
    try:
        command.encode()
    except ValueError as error:
        assert "final relay decisions" in str(error)
    else:
        raise AssertionError("pending decision must not be encoded")
