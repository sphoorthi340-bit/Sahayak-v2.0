# Sahayak v2.0

**Sahayak** is an adaptive, failure-aware LoRa mesh network for disaster-response communication in rural mountain and plains terrain.

The project uses ESP32 field nodes and 868 MHz-class LoRa radios to provide infrastructure-independent emergency messaging through multi-hop forwarding. The software roadmap begins with a reliable packet protocol and telemetry pipeline before adding adaptive routing, proactive connectivity-risk assessment, human-relay integration, and base-station triage.

## Current research direction

The core research direction is:

> Explainable multi-metric routing and proactive connectivity-risk assessment for a real ESP32–LoRa mesh under controlled traffic and node-failure conditions.

The proposed routing score combines signal quality, hop count, and queue load. The system will be compared against bounded flooding and RSSI-only routing using packet delivery ratio, latency, retries, route-recovery time, queue behavior, and energy measurements.

## Repository structure

```text
firmware/       ESP32 field-node firmware and shared protocol code
base_station/   Python gateway, parser, logger, topology, and analysis tools
experiments/    Reproducible scenarios and collected results
docs/           Protocol, pin map, test plan, and design decisions
hardware/       Hardware notes, wiring references, and node-build information
```

## Development status

The repository is currently at **Milestone 0: software foundation**. The first target is a two-node `HELLO -> ACK` exchange with machine-readable serial telemetry. Mesh forwarding and adaptive routing will be added only after this foundation is tested.

## Initial node roles

| Node role | Example ID | Responsibility |
|---|---:|---|
| Base station | 1 | Receives reports, sends acknowledgments, and later runs topology/risk logic |
| Relay node | 2–3 | Forwards packets between field nodes and the base |
| Field node | 4–6 | Generates emergency reports and sends status messages |
| Human-relay node | 7 | Supports manual corroboration and operator acknowledgment |
| Spare/test node | 8 | Used for debugging and failure experiments |

## Important engineering rules

1. Every packet must contain an origin ID and sequence number.
2. Every forwarded packet must have a TTL and duplicate-suppression mechanism.
3. Every dropped packet must have a recorded reason.
4. Every route must expire after a defined time.
5. Every experiment must record firmware version and radio configuration.
6. Radio frequency, antenna, and power settings must be confirmed for the exact hardware before outdoor testing.
7. Do not call the system machine-learning-based unless a trained and evaluated model is actually implemented.
8. Do not call graph redundancy recomputation physical node-lifetime prediction; use proactive connectivity-risk assessment unless a forecasting model is added.

## Getting started

Read these files first:

- [`docs/protocol.md`](docs/protocol.md)
- [`docs/neighbor_discovery.md`](docs/neighbor_discovery.md)
- [`docs/dynamic_routing.md`](docs/dynamic_routing.md)
- [`docs/reliability.md`](docs/reliability.md)
- [`docs/human_relay.md`](docs/human_relay.md)
- [`docs/priority_experiments.md`](docs/priority_experiments.md)
- [`docs/progress_and_hardware_report.md`](docs/progress_and_hardware_report.md)
- [`docs/friend_agent_handoff.md`](docs/friend_agent_handoff.md)
- [`docs/pin_map.md`](docs/pin_map.md)
- [`docs/test_plan.md`](docs/test_plan.md)
- [`docs/decisions.md`](docs/decisions.md)
- [`hardware/README.md`](hardware/README.md)
- [`hardware/bom.md`](hardware/bom.md)
- [`hardware/bringup_checklist.md`](hardware/bringup_checklist.md)
- [`base_station/README.md`](base_station/README.md)
- `base_station/data_quality.py`
- `base_station/experiment_runner.py`
- `base_station/report_generator.py`
- `base_station/commands.py`
- [`docs/software_first_status.md`](docs/software_first_status.md)
- [`docs/software_only_plan.md`](docs/software_only_plan.md)
- [`tests/README.md`](tests/README.md)
- [`tests/hardware/two_node_pair_test.md`](tests/hardware/two_node_pair_test.md)

The firmware scaffold is intentionally conservative. It does not yet implement the complete mesh algorithm. It establishes the packet format, serial telemetry, and a testable two-node communication foundation. The software-only simulator now supports deterministic routing comparisons and controlled failure-risk scenarios while physical hardware testing is postponed.
