# Route Reliability Milestone

## Route hysteresis

The firmware now remembers the current next hop in `gCurrentNextHop`. A new candidate must exceed the current candidate’s score by at least `kRouteHysteresisPoints` before the node switches routes. The default margin is 5 points on the firmware’s 0–100 score scale.

A route switch is immediate when the current route is absent, stale, unhealthy, or equal to the previous hop. This prevents hysteresis from preserving a broken route. When the current route remains valid and the improvement is small, the existing route is retained to reduce route churn.

## Hop-by-hop ACK tracking

Every transmitted `REPORT` is tracked in a bounded pending-transmission table. The key is `(origin_id, sequence)`. A relay tracks its forwarded copy, while the base station sends an ACK to the immediate sender. This allows each hop to confirm delivery to its next hop.

The current firmware uses:

```text
ACK timeout: configured by kAckTimeoutMs
Maximum retries: configured by kMaxRetries
Pending transmission capacity: 8
```

The retry counter increases only after a timeout. When the maximum is reached and the final timeout expires, the packet is removed from the pending table and `RETRY_LIMIT_REACHED` is emitted.

## Retry telemetry

Retry and exhaustion events include the packet origin, sequence number, next hop, hop count, TTL, queue length, and retry count. These fields are required for later PDR, latency, and route-recovery analysis.

## Reliability states

| Event | Expected behavior |
|---|---|
| Report transmitted | Add report to pending ACK table |
| Matching ACK received | Remove report from pending table and emit `ACKED` |
| ACK timeout before retry limit | Retransmit and increment retry counter |
| Final timeout after retry limit | Remove report and emit `RETRY_LIMIT_REACHED` |
| Current route becomes stale | Immediately permit a new route or emit `NO_ROUTE` |
| Candidate improves by less than hysteresis margin | Retain current route |
| Candidate improves by at least hysteresis margin | Switch to candidate |

## Important implementation boundary

This is hop-by-hop reliability, not yet complete end-to-end reliability. ACK path reversal and application-level duplicate semantics across the entire route are still limited. Hardware testing is required to determine whether the selected timeout is appropriate for the final LoRa settings and terrain.

The software tests validate state transitions and retry bookkeeping. They do not prove radio delivery probability or field performance.
