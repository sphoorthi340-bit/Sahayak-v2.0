# Software-First Development Status

## Current decision

Physical hardware testing is postponed. Development continues with protocol implementation, software simulation, base-station processing, routing logic, and reproducible experiment tooling.

## What can be validated now

The team can validate the following without hardware:

- Packet field definitions and parsing.
- Duplicate suppression rules.
- TTL and route-loop behavior.
- Route scoring and tie-breaking.
- Queue and priority policies.
- Node-disjoint path calculations.
- Connected, at-risk, and isolated state transitions.
- Base-station event logging.
- PDR, latency, retry, and duplicate metric calculations.
- Reproducible scenario execution.

## What cannot be claimed yet

Software simulation cannot establish actual LoRa range, RSSI distributions, SNR behavior, packet delivery under terrain obstruction, radio energy consumption, antenna performance, or field reliability. Simulated outputs are for debugging and algorithm development only.

The paper must clearly separate:

| Evidence type | Valid use |
|---|---|
| Unit tests | Demonstrate code and logic correctness |
| Deterministic simulation | Compare algorithm behavior under declared assumptions |
| Bench hardware tests | Measure real packet and timing behavior in controlled conditions |
| Field experiments | Support terrain, link, energy, and disaster-network claims |

## Simulation commands

From the repository root:

```bash
PYTHONPATH=. pytest -q base_station/tests tests/simulation
PYTHONPATH=. python3 -m simulation.run_comparison \
  experiments/scenarios/routing_comparison.json \
  --output experiments/processed_results/routing_comparison.csv
PYTHONPATH=. python3 -m simulation.run_failure_risk \
  experiments/scenarios/failure_risk.json \
  --output experiments/processed_results/failure_risk.csv
```

The generated result files are ignored by Git because experiment outputs should be stored separately with scenario metadata and raw logs.

## Hardware work to resume later

When the components arrive, resume from `tests/hardware/README.md` and `hardware/bringup_checklist.md`. The first physical goal remains a two-node `HELLO -> REPORT -> ACK` exchange. Do not jump directly to an eight-node field deployment.
