# Sahayak v2.0 First Two-Node Bring-Up Checklist

## Before powering anything

- [ ] Confirm the exact ESP32 board model for both nodes.
- [ ] Confirm both LoRa modules have the same frequency and module family.
- [ ] Confirm the antenna is matched to the radio frequency.
- [ ] Confirm the correct antenna connector is installed.
- [ ] Confirm radio voltage and logic-level requirements from the module documentation.
- [ ] Confirm common ground between ESP32 and LoRa module.
- [ ] Check for short circuits with a multimeter.
- [ ] Do not connect a battery until USB tests are complete.
- [ ] Do not transmit without the antenna connected.

## Flashing configuration

Flash one board as the base station and one as a field node.

| Physical board | Firmware setting |
|---|---|
| Base station | `kNodeId = 1` |
| Field node | `kNodeId = 2` |

The node ID is changed in `firmware/include/config.h`. Do not create separate copies of the firmware source for each node.

## Initial radio configuration

The repository currently uses conservative provisional values:

```text
frequency:       866.5 MHz provisional
bandwidth:       125 kHz
spreading factor: 7
coding rate:     4/5
transmit power:  14 dBm provisional
CRC:             enabled
```

These values must be confirmed against the purchased module and the applicable local radio rules before outdoor RF testing. The team should record the final values in the experiment log.

## Test sequence

1. Connect the first ESP32 to USB without the LoRa module.
2. Confirm that the board can be flashed and that serial output works at 115200 baud.
3. Wire the LoRa module according to `docs/pin_map.md`.
4. Attach the matched antenna before radio transmission.
5. Flash node 1 and node 2 with the same firmware and different node IDs.
6. Open separate serial monitors.
7. Confirm both nodes report successful radio initialization.
8. Wait for periodic `HELLO` events.
9. Send `r` from node 2’s serial monitor.
10. Confirm node 1 receives a `REPORT` event.
11. Confirm node 1 sends an `ACK`.
12. Confirm node 2 receives or logs the ACK outcome.
13. Save both serial logs with the firmware commit and radio settings.

## Failure checks

- [ ] Wrong frequency produces a documented failure rather than being silently assumed to work.
- [ ] Removing the antenna is never used as a casual test condition.
- [ ] Power brownouts are recorded and not mistaken for routing failures.
- [ ] Invalid packet input does not crash the node.
- [ ] The node remains responsive after an ACK timeout.
- [ ] The sequence number increases for each locally created report.

## Evidence to capture

For the first successful test, save:

```text
node_1_serial.log
node_2_serial.log
firmware_commit.txt
hardware_record.txt
radio_configuration.txt
photos_of_wiring/
```

The first milestone is complete only when the saved evidence can show a numbered report from its origin to the base station and a corresponding acknowledgment.
