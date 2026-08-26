# Sahayak Packet Protocol v0.1

## Purpose

This document defines the first interoperable packet format for Sahayak field nodes and the base-station gateway. The format is intentionally small and explicit so that firmware, logging, and experiments can be developed independently.

Version 0.1 supports point-to-point `HELLO`, `REPORT`, and `ACK` messages and now includes the first three-node forwarding behavior. Dynamic route advertisements and failure-risk messages remain future extensions, but the fields needed for them are included now.

## Node identifiers

Node IDs are unsigned 8-bit values.

| ID range | Meaning |
|---|---|
| `1` | Base station |
| `2–3` | Relay nodes |
| `4–6` | Field nodes |
| `7` | Human-relay node |
| `8` | Spare/test node |
| `255` | Broadcast or unknown |

## Radio configuration placeholder

The exact values must be frozen after the team confirms the purchased radio module and the applicable local operating rules.

```text
frequency_mhz       = 866.5
bandwidth_hz        = 125000
spreading_factor    = 7
coding_rate         = 5
transmit_power_dbm  = 14 (provisional; confirm module and local limit)
crc                 = enabled
sync_word           = project-specific
```

All nodes in one experiment must use the same radio configuration unless the experiment explicitly tests configuration differences.

## Packet header

The first firmware implementation uses a packed C++ structure with explicit fixed-width integer types. All multibyte integers use little-endian order because the initial nodes use the same ESP32 platform. If another MCU is added later, the serialization layer must be updated rather than relying on compiler memory layout.

| Field | Type | Size | Description |
|---|---|---:|---|
| `version` | `uint8_t` | 1 | Protocol version, currently `1` |
| `message_type` | `uint8_t` | 1 | `HELLO`, `REPORT`, `ACK`, etc. |
| `origin_id` | `uint8_t` | 1 | Node that created the packet |
| `sender_id` | `uint8_t` | 1 | Node currently transmitting |
| `destination_id` | `uint8_t` | 1 | Intended final destination |
| `previous_hop` | `uint8_t` | 1 | Immediate node that previously forwarded it |
| `sequence` | `uint32_t` | 4 | Monotonic origin sequence number |
| `route_version` | `uint16_t` | 2 | Route-table version, `0` until routing is added |
| `ttl` | `uint8_t` | 1 | Remaining forwarding budget |
| `hop_count` | `uint8_t` | 1 | Number of forwarding hops |
| `priority` | `uint8_t` | 1 | `0` low through `3` emergency |
| `payload_length` | `uint8_t` | 1 | Number of payload bytes |
| `created_uptime_ms` | `uint32_t` | 4 | Origin-node uptime at creation |
| `header_crc` | `uint16_t` | 2 | Header integrity field if enabled |

The maximum radio payload should remain small. The application must reject payloads larger than the configured maximum rather than silently truncating them.

## Message types

| Symbol | Value | Meaning |
|---|---:|---|
| `HELLO` | `1` | Neighbor discovery and health announcement |
| `REPORT` | `2` | Emergency report |
| `ACK` | `3` | Acknowledgment for a report or control packet |
| `STATUS` | `4` | Telemetry and node-state report |
| `ROUTE_UPDATE` | `5` | Route information |
| `FAILURE_RISK` | `6` | Proactive connectivity-risk warning |
| `COMMAND` | `7` | Base-station or operator command |

## Payloads

### HELLO payload

```text
node_state              uint8_t
battery_mv              uint16_t
queue_length            uint8_t
advertised_hop_count    uint8_t
neighbor_count          uint8_t
firmware_major          uint8_t
firmware_minor          uint8_t
```

### REPORT payload

```text
severity                uint8_t       0–5
people_affected         uint16_t
trapped_persons         uint16_t
confidence              uint8_t       0–5
region_id               uint8_t
report_code             uint8_t
text_or_data            bounded bytes
```

### ACK payload

```text
acknowledged_origin_id  uint8_t
acknowledged_sequence   uint32_t
ack_status              uint8_t
ack_sender_id           uint8_t
```

### STATUS payload

```text
node_state              uint8_t
battery_mv              uint16_t
queue_length            uint8_t
last_peer_rssi_dbm      int16_t
last_peer_snr_x10       int16_t
independent_path_count  uint8_t
route_version           uint16_t
```

## Packet identity and duplicate suppression

A packet is uniquely identified by `(origin_id, sequence)`. Each node maintains a bounded cache of recently observed packet identities. If an identity is already present, the packet is marked as a duplicate and is not forwarded again.

The cache must have an expiration period and a maximum size. The expiration value must be recorded in the experiment configuration.

## Forwarding rules

1. Reject packets with an unsupported protocol version.
2. Reject packets with invalid CRC or an impossible payload length.
3. Reject packets whose TTL is zero before forwarding.
4. Reject duplicates using `(origin_id, sequence)`.
5. Deliver the packet if `destination_id` matches the local node.
6. Forward the packet if a valid route exists and the local node is not the destination.
7. Decrement TTL and increment hop count before forwarding.
8. Record a reason code for every rejection or drop.
9. Do not forward indefinitely while waiting for an ACK.
10. Do not select a stale or unhealthy neighbor as the next hop.

## ACK and retry behavior

The first implementation uses bounded hop-by-hop acknowledgments.

```text
ACK_TIMEOUT_MS       = configurable
MAX_RETRIES          = configurable
FORWARD_BACKOFF_MS   = configurable
```

A sender retransmits only up to `MAX_RETRIES`. After the final timeout, it records `RETRY_LIMIT_REACHED` and reports the failure through telemetry. The exact values must be chosen after measuring airtime and tested under both quiet and burst traffic.

## Priority values

| Value | Meaning |
|---:|---|
| `0` | Routine/status |
| `1` | Low-priority report |
| `2` | Important report |
| `3` | Emergency report or failure warning |

The queue manager must prevent priority `3` traffic from permanently starving lower-priority reports. The starvation test is part of the base-station experiment plan.

## Serial telemetry format

The firmware emits machine-readable event records over USB serial. Each record is one line. The first version uses comma-separated key/value fields so the Python parser can be simple and human-readable.

```text
EVENT,t_ms=12345,node=3,type=REPORT,origin=5,seq=1042,prev=5,next=1,hop=1,ttl=7,rssi=-94,snr=7.1,queue=0,retry=0,state=FORWARDED,outcome=QUEUED
```

Every event should include at least:

```text
t_ms,node,type,origin,seq,prev,next,hop,ttl,rssi,snr,queue,retry,state,outcome
```

The parser must tolerate fields being absent in early messages but should mark them as missing rather than guessing values.

## Current implementation boundary

The first three-node forwarding implementation uses a static next hop configured in firmware. It supports TTL decrementing, duplicate suppression, bounded queueing, and explicit route-loop protection. It does not yet perform dynamic neighbor-based route selection or end-to-end ACK path reversal.

## Reserved future fields

The following features are intentionally not implemented in v0.1:

- Authenticated message MAC.
- Replay protection using persistent counters.
- Route advertisements.
- Node-disjoint path computation on the microcontroller.
- Human-relay corroboration semantics.
- Statistical physical node-failure prediction.

These features must extend the protocol without silently changing the meaning of existing fields.
