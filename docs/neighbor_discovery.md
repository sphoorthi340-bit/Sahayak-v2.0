# Neighbor Discovery and Route Expiry

## Purpose

This milestone gives each ESP32 node a small, time-bounded view of nearby nodes. Nodes periodically transmit `HELLO` packets. A receiver parses the HELLO payload, records the immediate sender and radio measurements, and expires the record when no fresh HELLO has arrived.

## Neighbor record

Each firmware neighbor record contains:

| Field | Meaning |
|---|---|
| `nodeId` | Immediate sender of the HELLO |
| `nodeState` | Sender’s advertised state |
| `batteryMv` | Sender’s reported battery value; currently zero until the monitor is added |
| `queueLength` | Sender’s current forwarding-queue estimate |
| `advertisedHopCount` | Sender’s known hop distance to the base, or `255` when unknown |
| `neighborCount` | Number of neighbors known by the sender |
| `firmwareMajor/minor` | Firmware compatibility information |
| `lastRssiDbm` | RSSI measured for the most recent HELLO |
| `lastSnrX10` | SNR multiplied by ten to preserve one decimal place without a float |
| `lastHeardMs` | Local receive time used for expiry |

The table is fixed-size to avoid dynamic memory allocation on the ESP32. The current capacity is 16 neighbors.

## Freshness rule

A record is fresh for 30 seconds after its most recent HELLO. The HELLO interval is currently 10 seconds, so a node should normally hear several announcements before expiry. If a node stops transmitting, disappears, loses power, or becomes unreachable, its record becomes stale and is removed.

The expiry check uses local uptime rather than wall-clock time. Nodes do not need synchronized clocks for this function.

## State behavior

| Condition | Local state |
|---|---|
| No HELLO has ever been received | `DISCOVER_NEIGHBORS` |
| Configured next hop is fresh and healthy | `CONNECTED` |
| Configured next hop is fresh but advertises degraded or unknown route health | `DEGRADED` |
| Configured next hop advertises an unhealthy state | `AT_RISK` |
| Configured next hop has expired or is absent | `ISOLATED` |
| Base station itself | `CONNECTED` |

The state is intentionally conservative. A fresh neighbor is not automatically treated as a valid end-to-end route unless it is the configured next hop for the current milestone.

## Current routing boundary

This implementation uses `kStaticNextHop` to preserve a controlled three-node test. For a line topology, configure the field node to use the relay ID and configure the relay to use the base-station ID. Dynamic next-hop selection will be implemented after the neighbor table has been verified on real nodes.

## Event evidence

When a HELLO is accepted, the node emits a machine-readable event containing the sender, RSSI, SNR, active-neighbor count, and current local state. When a report is generated, an expired configured next hop produces `NO_ROUTE` rather than silently transmitting to an unavailable route.

## Hardware validation later

The physical test must stop a node’s HELLO transmission, wait beyond the 30-second expiry interval, and verify that the peer transitions from connected/degraded to isolated or at-risk as appropriate. The test must save both serial logs and the firmware commit used.
