"""Create reproducible Sahayak experiment directories and metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from .data_quality import validate_metadata


SUBDIRECTORIES = ("raw", "processed", "plots")


def create_experiment(root: str | Path, experiment_id: str,
                      metadata: Mapping[str, object]) -> Path:
    """Create an experiment directory and write metadata.json."""
    if not experiment_id or "/" in experiment_id or "\\" in experiment_id:
        raise ValueError("experiment_id must be a simple non-empty name")
    issues = validate_metadata(metadata)
    errors = [issue.message for issue in issues if issue.severity == "ERROR"]
    if errors:
        raise ValueError("Invalid experiment metadata: " + "; ".join(errors))

    path = Path(root) / experiment_id
    path.mkdir(parents=True, exist_ok=False)
    for name in SUBDIRECTORIES:
        (path / name).mkdir()
    payload = dict(metadata)
    payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    (path / "metadata.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_metadata(experiment_path: str | Path) -> dict[str, object]:
    path = Path(experiment_path) / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8"))
