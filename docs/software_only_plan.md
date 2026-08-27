# Software-Only Development Plan

## Purpose

Sahayak can continue developing without physical nodes by using deterministic simulations, mock telemetry, saved-log replay, and placeholder hardware constants. These tools validate code paths and interfaces. They do not replace physical LoRa evidence.

## Allowed placeholder values

| Placeholder | Allowed use | Must not be claimed as |
|---|---|---|
| RSSI/SNR | Parser, route-scoring, and UI tests | Measured field link quality |
| Queue length | Queue and routing logic tests | Real congestion measurement |
| Hop count | Topology and routing scenarios | Field path measurement |
| Battery/current | Schema and analysis pipeline tests | Actual energy consumption |
| Node failure time | Controlled simulation and recovery tests | Real hardware failure behavior |
| Service time | Priority-surge simulation | Base-station or radio latency |
| Terrain/position | Scenario metadata and fixture tests | Field deployment conditions |

Synthetic records must be labelled `source=synthetic` or `scenario_id=synthetic-*`. Hardware logs must contain a firmware commit, hardware identity, radio settings, node positions, and collection metadata.

## Work that can be completed now

The following work does not require physical nodes:

1. Complete packet parser and schema compatibility.
2. Add protocol fixtures for every message type.
3. Test packet corruption and malformed telemetry.
4. Add replay of serial logs into SQLite.
5. Add route-scoring and hysteresis sweeps.
6. Add ACK/retry state-machine simulation.
7. Add route-recovery and warning-lead-time analysis.
8. Add priority, fairness, and human-relay simulations.
9. Add experiment-folder generation and metadata validation.
10. Add paper-table and plot generation from processed logs.
11. Add firmware unit-testable helpers where hardware-independent.
12. Add OLED and keypad interface abstractions with serial fallbacks.
13. Add protocol-level human-relay commands before radio integration.
14. Add data-quality checks that reject incomplete experiment runs.
15. Improve documentation, CI, and reproducibility.

## Work that requires physical nodes

The following cannot be honestly completed with placeholders alone:

- Real packet delivery ratio.
- Real end-to-end radio latency.
- Real RSSI/SNR under terrain and obstructions.
- Antenna and power behavior.
- Actual current and energy per delivered packet.
- Radio collision behavior.
- Physical route hysteresis and churn.
- Physical ACK/retry timing calibration.
- Multihop relay performance.
- Five-to-eight-node scalability.
- Field failure and recovery behavior.

## Current replay fixture

`tests/fixtures/synthetic_pair.log` is a clearly labelled synthetic event log. It is processed by the same parser and SQLite logger intended for real gateway output:

```bash
PYTHONPATH=. python3 -m base_station.replay \
  tests/fixtures/synthetic_pair.log \
  --database experiments/processed_results/synthetic_pair.sqlite \
  --scenario-id synthetic-pair
```

The resulting database is for software testing only. Do not place it in a paper’s hardware-results directory.

## Recommended continuation order

Continue software implementation in this order:

```text
protocol fixtures
    ↓
replay and data-quality validation
    ↓
ACK/retry simulator
    ↓
route-scoring and hysteresis sweeps
    ↓
priority and human-relay command semantics
    ↓
report and plot generation
    ↓
physical pair validation
    ↓
three-node and larger field experiments
```

The project should remain honest and reproducible: placeholders are useful for building the system, but only real hardware logs can support the final networking and paper claims.
