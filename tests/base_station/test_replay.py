from pathlib import Path
import sqlite3

from base_station.replay import replay


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_pair.log"


def test_replay_stores_only_event_lines(tmp_path):
    database = tmp_path / "replay.sqlite"
    count = replay(FIXTURE, database, scenario_id="synthetic-pair")
    assert count == 8
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT COUNT(*), MIN(scenario_id), MAX(event_type) FROM events"
        ).fetchone()
    finally:
        connection.close()
    assert rows == (8, "synthetic-pair", "REPORT")
