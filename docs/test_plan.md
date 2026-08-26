# Sahayak Software Test Plan

## Test principles

Every feature must have a reproducible test. Test records must include the firmware commit, node IDs, radio settings, topology, traffic count, failure condition, and raw logs.

A successful visual demonstration is not sufficient for the final paper. The experiment system must preserve both successful and failed packet events.

## Milestone tests

### T01: Radio initialization

**Procedure:** Flash the firmware and boot a node with the configured radio and antenna.

**Pass criteria:** The node initializes without hanging, reports its firmware start event, and enters receive mode.

### T02: HELLO exchange

**Procedure:** Run two nodes for at least five minutes.

**Pass criteria:** Periodic `HELLO` packets are visible in both serial outputs, and the events contain node ID, sequence number, and timestamp.

### T03: REPORT and ACK

**Procedure:** Generate 100 reports from one node using the serial `r` command or emergency button.

**Pass criteria:** The receiver logs valid reports, sends ACKs, and the sender records ACK or timeout outcomes without crashing.

### T04: Invalid packet handling

**Procedure:** Feed truncated, wrong-version, and oversized frames to the decoder.

**Pass criteria:** Invalid frames are rejected and logged as `INVALID`; the node remains operational.

### T05: Three-node forwarding

**Procedure:** Place a source, relay, and base station in a line topology.

**Pass criteria:** Reports arrive at the base through the relay, packet IDs are preserved, and packets do not circulate indefinitely.

### T06: Duplicate suppression

**Procedure:** Deliver the same packet identity to a relay more than once.

**Pass criteria:** The relay does not forward the duplicate more than once and records the duplicate outcome.

### T07: Retry and timeout behavior

**Procedure:** Disable or move the receiver during a report exchange.

**Pass criteria:** The sender retries only up to the configured limit and records a final failure reason.

### T08: Route comparison

**Procedure:** Run identical traffic under bounded flooding, RSSI-only routing, and combined routing.

**Pass criteria:** Each configuration produces machine-readable results with identical scenario metadata.

### T09: Failure-risk assessment

**Procedure:** Disable relay nodes and rebuild topology from recent status messages.

**Pass criteria:** The system identifies connected, at-risk, and isolated conditions using independent-path logic.

## Required metrics

- Packet delivery ratio.
- End-to-end latency.
- Hop count.
- Retry count.
- Duplicate count.
- Queue delay.
- Route changes.
- Route-recovery time.
- Independent-path count.
- Warning lead time.
- False-positive and false-negative counts.
- Current or energy per delivered packet when measurement hardware is available.

## Experiment record template

```text
scenario_id:
firmware_commit:
protocol_version:
node_ids:
node_roles:
radio_frequency:
bandwidth:
spreading_factor:
coding_rate:
transmit_power:
topology_description:
node_coordinates:
traffic_count:
traffic_interval:
failure_condition:
weather_or_obstructions:
raw_log_path:
analysis_script_commit:
notes:
```
