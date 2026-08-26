# Sahayak Firmware

## Current milestone

The current firmware scaffold implements:

- ESP32 and LoRa initialization.
- Protocol v0.1 packet encoding and decoding.
- Periodic `HELLO` packets.
- Button- or serial-triggered `REPORT` packets.
- Direct packet delivery and ACK generation.
- Three-node forwarding queue with TTL decrementing.
- Fixed-size duplicate suppression cache.
- Priority-aware queueing and explicit route-loop/queue-full outcomes.
- Fixed-size neighbor table populated from `HELLO` packets.
- RSSI/SNR and advertised-hop tracking for each fresh neighbor.
- 30-second stale-neighbor expiry.
- `DISCOVER_NEIGHBORS`, `CONNECTED`, `DEGRADED`, `AT_RISK`, and `ISOLATED` route-health states.
- Route hysteresis using a configurable score-improvement margin.
- Hop-by-hop report ACK tracking, bounded retries, timeout handling, and retry-exhaustion telemetry.
- Radio CRC enablement.
- RSSI and SNR telemetry.
- Machine-readable serial `EVENT` records.

Dynamic multi-metric next-hop selection, route hysteresis, and hop-by-hop report ACK/retry behavior are now implemented. Physical hardware testing is still required to calibrate the timeout, verify ACK paths, and measure real packet loss.

## Build with PlatformIO

From the repository root:

```bash
pio run -d firmware
```

To upload a node:

```bash
pio run -d firmware -t upload
pio device monitor -d firmware
```

Set the node identity and pins in [`include/config.h`](include/config.h) before flashing. The current default node ID is `2`; the base station should use node ID `1`.

## First test

1. Connect a matched antenna to each radio.
2. Power two nodes from stable USB supplies.
3. Flash one node as ID `1` and the other as ID `2`.
4. Confirm both nodes print a successful radio initialization message.
5. Observe periodic `HELLO` events.
6. Send `r` in the serial monitor of the field node to create a report.
7. Verify that the base node receives the report and generates an ACK.
8. Save the serial output for the experiment log.

## Serial commands

| Command | Behavior |
|---|---|
| `h` | Send a `HELLO` packet immediately |
| `r` | Send an emergency test report |

## Important limitations

The current firmware no longer requires a static next hop for normal report forwarding. `kStaticNextHop` remains in the configuration as a reference for the original three-node test, while the active selector uses fresh-neighbor metrics and the configured routing weights.
