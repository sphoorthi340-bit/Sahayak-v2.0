from base_station.experiment_runner import create_experiment, load_metadata


def valid_metadata():
    return {
        "experiment_id": "pair-001",
        "source": "synthetic",
        "firmware_commit": "abc123",
        "node_ids": [1, 2],
        "radio_settings": {"frequency": 866500000},
        "node_positions": {"1": [0, 0], "2": [1, 0]},
    }


def test_create_experiment_writes_reproducible_layout(tmp_path):
    path = create_experiment(tmp_path, "pair-001", valid_metadata())
    assert (path / "metadata.json").exists()
    assert (path / "raw").is_dir()
    assert (path / "processed").is_dir()
    assert (path / "plots").is_dir()
    assert load_metadata(path)["experiment_id"] == "pair-001"


def test_create_experiment_rejects_invalid_metadata(tmp_path):
    try:
        create_experiment(tmp_path, "bad", {"source": "hardware"})
    except ValueError as error:
        assert "Invalid experiment metadata" in str(error)
    else:
        raise AssertionError("invalid metadata must be rejected")
