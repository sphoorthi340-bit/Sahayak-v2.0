# Dynamic Next-Hop Selection

## Purpose

The firmware now selects the next hop from the current neighbor table instead of always using `kStaticNextHop`. The selection is explainable and uses three measurements already present in the HELLO payload or received radio metadata:

- **RSSI:** stronger received signal is preferred.
- **Advertised hop count:** a neighbor with a shorter known path to the base is preferred.
- **Queue length:** a neighbor with less forwarding backlog is preferred.

The algorithm is a routing heuristic, not machine learning. It is deliberately deterministic so the team can compare it against RSSI-only and other baselines.

## Candidate filtering

A neighbor is eligible only when all of the following hold:

1. The record exists in the bounded neighbor table.
2. The record is fresh; it has been heard within 30 seconds.
3. The neighbor is not the local node.
4. The neighbor is not the packet’s previous hop.
5. The neighbor advertises `CONNECTED` or `DEGRADED`.
6. The neighbor has a known advertised hop count.

The previous-hop exclusion prevents an immediate two-node bounce. The expiry rule prevents a node from selecting a route based on old telemetry.

## Normalized score

Each component is converted to an integer score from 0 to 100:

```text
rssi_score  = clamp((RSSI_dBm + 120) × 100 / 55, 0, 100)
hop_score   = 100 / (advertised_hop_count + 1)
queue_score = 100 / (queue_length + 1)
```

The combined score is:

```text
score =
    (rssi_weight  × rssi_score
   + hop_weight   × hop_score
   + queue_weight × queue_score)
   / (rssi_weight + hop_weight + queue_weight)
```

The current firmware defaults are:

```text
RSSI weight:  50
Hop weight:   25
Queue weight: 25
```

The values are configured in `firmware/include/config.h`. The weights do not need to sum to 100 because the firmware normalizes by their total.

## Deterministic tie-breaking

If two candidates have the same integer score, the firmware chooses in this order:

1. Lower advertised hop count.
2. Stronger RSSI.
3. Lower queue length.
4. Lower node ID.

This makes repeated experiments reproducible and avoids route changes caused only by iteration order.

## Fallback behavior

If no eligible neighbor exists, the selector returns broadcast/unknown and the node records `NO_ROUTE`. A report is not silently sent through the old static next hop. This is important for route-expiry correctness.

## Research comparison modes

The software and later firmware experiments should compare at least:

| Mode | RSSI weight | Hop weight | Queue weight |
|---|---:|---:|---:|
| RSSI-only baseline | 100 | 0 | 0 |
| RSSI + hop | 70 | 30 | 0 |
| Proposed adaptive mode | 50 | 25 | 25 |

The radio settings, placement, traffic pattern, packet count, and failure event must remain unchanged across modes. Only the route-selection rule should change.

## Current limitation

The advertised hop count is learned from HELLO messages and is therefore only as accurate as the sender’s own route state. The current milestone does not yet implement a full route-advertisement protocol, end-to-end path confirmation, or hysteresis. The next refinement should add route stability/hysteresis so a node does not switch routes for very small score differences.
