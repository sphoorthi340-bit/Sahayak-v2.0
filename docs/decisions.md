# Sahayak Architecture Decisions

## ADR-001: Use a modular ESP32 plus 868 MHz-class LoRa radio

The first research prototype uses a standard ESP32 development board with a separate 868 MHz-class LoRa breakout. This keeps the controller, radio, display, and measurement layers replaceable and easier to debug.

The exact radio module and antenna must be recorded before outdoor testing. Generic module names such as “SX1278 LoRa” are not sufficient; frequency must be verified from the actual board.

## ADR-002: Build direct communication before mesh routing

Protocol v0.1 first supports direct `HELLO`, `REPORT`, and `ACK` exchange. Forwarding and route selection are deliberately disabled until the two-node test is stable. This separates radio and protocol bugs from mesh-routing bugs.

## ADR-003: Use explicit serialization

The wire format is serialized field by field in `protocol.cpp`. The system must not depend on compiler struct padding or memory layout. Version 0.1 uses little-endian multibyte integers because the first nodes use the same ESP32 platform.

## ADR-004: Use packet identity `(origin_id, sequence)`

Every packet must be uniquely identifiable for duplicate suppression, retry analysis, and end-to-end tracing.

## ADR-005: Start with explainable routing

The proposed routing score combines normalized RSSI, hop count, and queue load. Weights are configurable and must be recorded in experiment metadata. Machine learning is postponed until a reliable telemetry dataset and a defensible baseline exist.

## ADR-006: Use proactive connectivity-risk terminology initially

The initial failure module recomputes current path redundancy from status and link observations. It is called proactive connectivity-risk assessment rather than physical node-lifetime prediction. The terminology may be revised only if a validated forecasting model is added.

## ADR-007: Keep the base station simple first

The first base station is a Python command-line receiver with SQLite logging. A dashboard is optional and comes after the data pipeline and experiment reproducibility are stable.

## ADR-008: Log failures as carefully as successes

Invalid packets, duplicates, no-route outcomes, TTL expiry, queue overflow, and retry exhaustion must be retained. Failure records are necessary for debugging and for honest paper evaluation.

## ADR-009: Freeze the first procurement baseline

The team will proceed with ESP32 DevKit-class boards, explicitly verified 868 MHz SX1276-class LoRa radios, matched antennas, SSD1306 OLED displays, emergency buttons, status indicators, and stable USB power for the initial bring-up. Batteries, charging circuits, enclosures, and current monitors will be introduced after the two-node communication milestone is stable. The detailed checklist is maintained in `hardware/bom.md`.
