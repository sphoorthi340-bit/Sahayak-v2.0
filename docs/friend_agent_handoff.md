# Sahayak v2.0 Friend and Agentic-AI Handoff Guide

**Repository:** [github.com/sphoorthi340-bit/Sahayak-v2.0](https://github.com/sphoorthi340-bit/Sahayak-v2.0)  
**Repository status:** Private  
**Project lead:** Shashank Spoorthi  
**Primary embedded owner:** Shashank Spoorthi  
**Friend’s role:** Base-Station, Data, Experimentation, Human-Relay, and Research-Evidence Lead

## 1. Purpose of this document

This document is written for two audiences: the human teammate who will own the base-station and research-evidence side of Sahayak, and any future agentic AI that helps that teammate continue the work. It explains what Sahayak is, what the project lead has already done, what the teammate owns from now until completion, how the repository should be used, and what rules must not be violated.

The teammate should be able to read this document and begin work without needing a separate explanation. A future AI should read this document before editing code, inspect the repository, run the existing tests, preserve the current behavior, and then continue only from the documented backlog.

## 2. What Sahayak is

Sahayak is a LoRa-based disaster-response communication system intended for terrain-constrained rural and mountainous regions. It uses ESP32-based nodes and LoRa radios to support emergency reports over a multi-hop network when normal communication infrastructure is unavailable or unreliable.

The proposed research contribution combines four elements:

1. Explainable adaptive routing using RSSI, hop count, and queue length.
2. Proactive connectivity-risk assessment based on fresh neighbor information and independent paths to the base station.
3. Human relay nodes as a first-class protocol and decision layer rather than only a user interface.
4. Real hardware and field validation against bounded flooding and single-metric routing baselines.

The system is not yet a finished field-proven network. The software prototype is advanced, but real radio, terrain, energy, and failure evidence still has to be collected.

## 3. What the project lead has already completed

The project lead owns the embedded side and has already created the main technical foundation.

### Repository and process

The repository has a structured layout for firmware, base-station code, simulation, experiments, hardware information, tests, and documentation. It uses PlatformIO for ESP32 firmware builds and GitHub Actions for Python test execution. The repository is currently private and should remain private while development and unpublished experiments continue.

### Firmware and protocol foundation

The firmware currently includes:

- ESP32–LoRa initialization.
- Shared packet serialization and deserialization.
- `HELLO`, `REPORT`, `ACK`, `STATUS`, `ROUTE_UPDATE`, `FAILURE_RISK`, and `COMMAND` message vocabulary.
- Packet version, origin ID, sender ID, destination ID, previous hop, sequence number, TTL, hop count, priority, route version, payload length, and creation uptime fields.
- Three-node forwarding foundations.
- TTL decrementing and hop-count incrementing.
- Duplicate suppression.
- Bounded priority forwarding queue.
- Route-loop protection.
- Explicit forwarding outcomes such as `NO_ROUTE`, `TTL_EXPIRED`, `DUPLICATE`, `QUEUE_FULL`, and `ROUTE_LOOP`.

### Neighbor discovery and route selection

The firmware maintains a fixed-size neighbor table populated by periodic `HELLO` messages. It tracks freshness, RSSI, SNR, queue length, advertised hop count, neighbor state, and last-heard time. Stale neighbors expire after the configured freshness timeout.

Dynamic next-hop selection uses fresh and healthy neighbor records. Its score combines:

```text
route_score =
    RSSI_weight  × RSSI_score
  + hop_weight   × hop_score
  + queue_weight × queue_score
```

The current default weights are RSSI 50, hop count 25, and queue length 25. The implementation has deterministic tie-breaking and route hysteresis so the node does not switch routes for insignificant score changes.

### Reliability

The firmware includes a pending-ACK table for report packets, ACK matching using origin and sequence number, bounded retry scheduling, ACK timeout handling, and retry-exhaustion telemetry. The implementation is hop-by-hop reliability. It is not yet a complete end-to-end reliability protocol.

### Software analysis already available

The repository contains:

- Python packet parser.
- SQLite event logger.
- Routing and forwarding primitives.
- Node-disjoint topology utilities.
- Connectivity-risk and route-recovery measurements.
- Priority triage.
- Fairness-aware queue logic.
- Human-relay decision semantics.
- Deterministic routing comparison simulation.
- Deterministic failure-risk simulation.
- Deterministic priority-surge simulation.

### Validation already completed

At the latest handoff point:

- 36 Python tests pass.
- ESP32 firmware compiles successfully with PlatformIO.
- Routing comparison simulation runs successfully.
- Failure-risk simulation runs successfully.
- Priority-surge simulation runs successfully.
- The Git working tree is clean.
- The latest pushed commit is `c16f1fd Add two-node hardware progress report`.

These are software validations. They are not evidence that the physical LoRa network works in the field.

## 4. The teammate’s complete role

The teammate should take the title:

> **Base-Station, Data, Experimentation, Human-Relay, and Research-Evidence Lead.**

The teammate is not only a Python developer or dashboard developer. The teammate owns the complete measurement and evidence pipeline:

```text
Gateway ESP32
    ↓ USB serial
Serial receiver
    ↓
Event parser
    ↓
SQLite/raw logs
    ↓
Topology and risk analysis
    ↓
Priority and human-relay decisions
    ↓
Metrics and plots
    ↓
Experiment summary
    ↓
Paper tables and figures
```

## 5. Teammate responsibilities through the entire project

### Requirements and measurement design

The teammate converts project ideas into measurable requirements. For every proposed feature, the teammate should ask what event must be logged, what metric proves it, what baseline is required, and what experiment will reproduce it.

Examples include:

| Feature claim | Required evidence |
|---|---|
| Adaptive routing is better | Same scenario under RSSI-only and adaptive routing |
| Queue-aware routing reduces congestion | Queue length, waiting time, and retry records |
| Risk warning is proactive | Warning time before a controlled connectivity failure |
| Human relay adds value | Automated-only versus human-assisted comparison |
| System works in terrain | Controlled placements and mixed-terrain runs |
| System is energy-aware | Current and voltage data per delivered packet |

### Protocol compatibility

The teammate owns the base-station data contract. Whenever the firmware protocol changes, the teammate must update the parser, schema, sample logs, tests, and documentation. No protocol field should be silently ignored.

The teammate should maintain compatibility with these message types:

| Message | Teammate’s responsibility |
|---|---|
| `HELLO` | Parse health, queue, route, and freshness data |
| `REPORT` | Store emergency metadata and arrival timing |
| `ACK` | Match acknowledgment to origin and sequence |
| `STATUS` | Store node and link telemetry |
| `ROUTE_UPDATE` | Reconstruct route changes |
| `FAILURE_RISK` | Record warning state and timing |
| `COMMAND` | Generate operator or test commands |

### Base-station software

The teammate should maintain:

- Serial receiver.
- Event parser.
- SQLite logger.
- CSV/JSON export.
- Raw-log preservation.
- Topology reconstruction.
- Connectivity-risk analysis.
- Route-recovery analysis.
- Priority queue.
- Human-relay decision manager.
- Metrics scripts.
- Plot generation.
- Experiment-runner integration.

The current base-station modules are:

```text
base_station/main.py
base_station/packet_parser.py
base_station/logger.py
base_station/metrics.py
base_station/analyze_results.py
base_station/topology.py
base_station/routing.py
base_station/forwarding.py
base_station/reliability.py
base_station/recovery.py
base_station/priority_engine.py
base_station/fair_queue.py
base_station/human_relay.py
```

### Topology and risk analysis

The teammate should build a time-varying network graph from HELLO, STATUS, and forwarding events. The graph should represent node presence, link freshness, RSSI, SNR, advertised hop count, queue length, current next hop, route switches, independent paths, at-risk nodes, and isolated nodes.

The teammate must distinguish node-disjoint and edge-disjoint paths. Two paths that share the same relay are not two independent relay paths for failure tolerance.

### Routing evaluation

The teammate must compare routing strategies fairly:

1. Bounded flooding.
2. RSSI-only routing.
3. RSSI plus hop count.
4. RSSI plus hop count plus queue length.
5. The full adaptive strategy with hysteresis.

Every comparison must keep packet payload, node placement, traffic pattern, radio settings, transmit power, failure event, and experiment duration constant. Only the routing strategy should change.

### Priority and congestion evaluation

The teammate owns the queue experiment. The current software supports FIFO, priority, and fairness-aware aging behavior. The teammate should measure delivery count, waiting time by priority class, 95th-percentile waiting time, queue overflow, priority inversion, and routine-report starvation.

The current files are:

```text
base_station/priority_engine.py
base_station/fair_queue.py
experiments/priority_surge.py
experiments/scenarios/priority_surge.json
docs/priority_experiments.md
```

### Human-relay evaluation

The teammate owns the meaning and workflow of the human relay. A report enters a pending state, an operator reviews it, and the operator may corroborate, reject, or escalate it. The action and operator note must be logged.

The current actions are:

- `PENDING`.
- `CORROBORATED`.
- `REJECTED`.
- `ESCALATED`.

The teammate must compare automated-only handling against human-assisted handling. A human-relay screen without a measurable effect on queue priority, response ordering, or false-alert behavior is not enough for the paper.

The current implementation is:

```text
base_station/human_relay.py
docs/human_relay.md
```

### Experiment automation

The teammate should maintain scenario files and experiment runners that can configure packet count, traffic rate, priority distribution, routing strategy, failure time, recovery time, node positions, and output directory.

Each experiment should produce a self-contained directory:

```text
experiments/results/<experiment_id>/
├── metadata.json
├── raw/
├── processed/
├── plots/
└── summary.md
```

### Hardware measurement support

When the current two-node pair is tested, the teammate should operate the logger and evidence process while the project lead operates the embedded nodes. The teammate must record the firmware commit, node IDs, board and radio models, radio settings, antenna information, node position, separation, power source, packet count, environment, and deliberate failure events.

The teammate should not label a test successful from an LED or OLED alone. The success must be reconstructable from the saved serial logs and metadata.

### Paper and research evidence

The teammate leads the experimental methodology, results, plots, tables, and limitations sections of the paper. The project lead leads the hardware architecture, firmware, protocol, routing, reliability, and embedded implementation sections.

The teammate must ensure that every number in the paper can be traced to raw logs, an experiment scenario, a firmware commit, and a documented analysis script.

## 6. What the project lead is doing

The project lead is responsible for:

- ESP32 and LoRa firmware.
- Packet encoding and decoding.
- Embedded state machine.
- Neighbor discovery implementation.
- Dynamic route selection.
- Route hysteresis.
- ACK/retry behavior.
- Queue and duplicate handling in firmware.
- OLED and keypad firmware integration.
- Hardware wiring and node assembly.
- Radio and power debugging.
- Physical node operation.
- Node placement during field tests.
- Embedded sections of the paper.

The teammate should not duplicate this work unnecessarily. Instead, the teammate should provide test inputs, logs, analysis requirements, and integration feedback.

## 7. Immediate state of the hardware pair

The project currently has two ESP32 boards, two OLEDs, two keypads, and other materials for a pair. If the pair also includes two compatible 868 MHz LoRa modules and two matched antennas, it can perform the first real RF tests.

The pair should be configured as:

| Node | ID | Role |
|---|---:|---|
| Node A | 1 | Base station |
| Node B | 2 | Field/report node |

The pair can validate direct HELLO discovery, direct REPORT delivery, ACK matching, retries, timeout behavior, RSSI/SNR logging, neighbor expiry, OLED display, keypad input, and base-station logging.

The pair cannot validate a real relay path, independent-path redundancy, cascading failures, five-to-eight-node scalability, or terrain-constrained multihop performance.

The complete procedure is in:

```text
tests/hardware/two_node_pair_test.md
docs/progress_and_hardware_report.md
```

## 8. Recommended work order for the teammate

The teammate should use this order:

1. Read this document, `README.md`, `docs/protocol.md`, `docs/reliability.md`, and `docs/progress_and_hardware_report.md`.
2. Run the complete Python test suite.
3. Run the routing, failure-risk, and priority-surge scenarios.
4. Inspect parser, logger, metrics, topology, reliability, recovery, priority, and human-relay modules.
5. Create and validate sample event logs.
6. Add experiment metadata handling.
7. Add a clean results-directory generator.
8. Add route-recovery and warning-lead-time summaries.
9. Add experiment plots and summary export.
10. Prepare the serial-log workflow for the two-node test.
11. When hardware is tested, process the real logs without mixing them with simulation data.
12. Prepare paper-ready tables only after data quality is verified.

## 9. Commands to use

From the repository root:

```bash
# Run all Python tests
PYTHONPATH=. pytest -q base_station/tests tests/simulation

# Run the routing comparison
PYTHONPATH=. python3 -m simulation.run_comparison \
  experiments/scenarios/routing_comparison.json \
  --output experiments/processed_results/routing_comparison.csv

# Run failure-risk analysis
PYTHONPATH=. python3 -m simulation.run_failure_risk \
  experiments/scenarios/failure_risk.json \
  --output experiments/processed_results/failure_risk.csv

# Run the priority-surge experiment
PYTHONPATH=. python3 experiments/priority_surge.py \
  experiments/scenarios/priority_surge.json \
  --output experiments/processed_results/priority_surge.csv

# Build the firmware
pio run -d firmware
```

The exact command-line options should be checked in the current script before adding automation around them.

## 10. Strict rules for a future agentic AI

A future agentic AI must follow these rules before editing:

1. Inspect the repository status and recent commit history.
2. Read this handoff guide and the relevant module documentation.
3. Run the existing tests before making changes.
4. Preserve the current packet protocol unless a change is explicitly justified.
5. Never delete or rewrite working modules merely to simplify the project.
6. Add tests for every new routing, logging, triage, reliability, or analysis behavior.
7. Run Python tests and firmware compilation before committing.
8. Keep simulation and hardware data strictly separate.
9. Never describe simulated PDR, latency, energy, or reliability as field measurements.
10. Never claim hardware testing occurred without saved logs or an explicit user report.
11. Never claim the system predicts physical node death unless a validated forecasting model exists.
12. Use “proactive connectivity-risk assessment” for graph-based warning logic.
13. Never add credentials, Wi-Fi passwords, API keys, or private data to the repository.
14. Preserve raw experiment logs and metadata.
15. Update documentation when behavior or protocol changes.
16. Make small, descriptive commits.
17. Do not introduce machine learning merely to make the project sound more AI-based.
18. Do not build a dashboard before the logging and analysis pipeline is reliable.
19. Do not change radio frequency or transmit-power defaults casually.
20. Ask the human user for exact board, radio, antenna, keypad, or OLED details when those details affect hardware code.

## 11. Agentic-AI bootstrap prompt

The following prompt may be copied into another agentic AI together with this document:

> You are assisting with the Sahayak v2.0 project in the private GitHub repository `sphoorthi340-bit/Sahayak-v2.0`. Read `docs/friend_agent_handoff.md` first, then inspect the repository and run the existing tests. You are responsible for the Base-Station, Data, Experimentation, Human-Relay, and Research-Evidence work. The project lead owns ESP32/LoRa firmware, embedded routing, hardware wiring, and physical node operation. Preserve the existing packet protocol and test behavior. Implement changes incrementally, add tests, run Python tests and PlatformIO firmware compilation when relevant, and update documentation. Keep simulation results separate from hardware evidence. Never claim a physical result unless the user provides logs or confirms the test. Your next work should focus on reproducible experiment folders, real-log ingestion, route-recovery metrics, priority/fairness evaluation, human-relay command semantics, and paper-ready result generation.

## 12. Definition of completion for the teammate

The teammate’s work is complete when:

- The base station reliably receives and stores all firmware events.
- Raw logs and metadata are preserved for every experiment.
- Topology and independent-path analysis are reproducible.
- Routing baselines and adaptive routing are compared fairly.
- Retry, route-switch, queue, and recovery metrics are automated.
- Priority and fairness behavior is measured under report surges.
- Human-relay actions are represented, transmitted when appropriate, and evaluated.
- Two-node, three-node, and larger hardware logs can be processed without manual rewriting.
- Every paper table and plot can be regenerated from repository code and saved data.
- Limitations, excluded runs, and failed experiments are documented honestly.

## 13. Final message to the teammate

Sahayak is already more than an idea, but it is not yet a completed research system. The project lead has built the embedded and algorithmic foundation. Your role is to make the system measurable, reproducible, experimentally defensible, and publishable.

Do not judge success only by whether a packet appears on an OLED. Your job is to answer what happened, why it happened, how often it happened, whether the routing strategy improved it, whether the warning came early enough, and whether another researcher can reproduce the result.
