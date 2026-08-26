# Sahayak Firmware

## Current milestone

The current firmware scaffold implements:

- ESP32 and LoRa initialization.
- Protocol v0.1 packet encoding and decoding.
- Periodic `HELLO` packets.
- Button- or serial-triggered `REPORT` packets.
- Direct packet delivery and ACK generation.
- Radio CRC enablement.
- RSSI and SNR telemetry.
- Machine-readable serial `EVENT` records.

Mesh forwarding and dynamic route selection are intentionally disabled until the direct two-node test is successful.

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

The first milestone uses direct transmission. A packet received by a node that is not its destination is currently reported as `NO_ROUTE` rather than forwarded. This is deliberate: forwarding will be implemented and tested as a separate milestone after the packet path is understood.
