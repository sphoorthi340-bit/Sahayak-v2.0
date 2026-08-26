"""Summarize Sahayak experiment-result CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def summarize(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    if data.empty:
        return pd.DataFrame()

    data["delivered"] = data["delivered"].astype(int)
    summary = data.groupby("strategy", as_index=False).agg(
        packets=("packet_id", "count"),
        delivered=("delivered", "sum"),
        mean_latency_ms=("latency_ms", "mean"),
        median_latency_ms=("latency_ms", "median"),
        mean_hops=("hops", "mean"),
        total_retries=("retries", "sum"),
    )
    summary["packet_delivery_ratio"] = summary["delivered"] / summary["packets"]
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Sahayak results")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = summarize(args.input)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(args.output, index=False)
        print(f"Wrote summary to {args.output}")
    else:
        print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
