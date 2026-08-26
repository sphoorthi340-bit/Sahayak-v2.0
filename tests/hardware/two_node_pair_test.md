# Two-Node Pair Test: ESP32, OLED, Keypad, and LoRa

## Goal

Validate the first physical Sahayak pair before expanding to a relay mesh. The pair consists of Node 1 as the base station and Node 2 as the field/report node.

## Required hardware

- Two ESP32 boards.
- Two verified 868 MHz SX1276-class LoRa modules, if RF testing is being performed.
- Two matched antennas, if RF testing is being performed.
- Two OLED modules.
- Two keypads or keypad input assemblies.
- Two USB cables and stable USB power.
- Jumper wires, breadboards, resistors, and a multimeter.

If the two LoRa modules or matched antennas are not available, perform only the ESP32, OLED, keypad, and serial-protocol tests. Do not transmit RF without the correct radio and antenna.

## Configuration

| Board | Node ID | Role |
|---|---:|---|
| Board A | 1 | Base station |
| Board B | 2 | Field/report node |

Use the same firmware source and change only `kNodeId` in `firmware/include/config.h` before each flash.

## Test order

### A. ESP32-only test

1. Connect each ESP32 to USB without peripherals.
2. Flash the firmware.
3. Confirm stable boot and serial output at 115200 baud.
4. Record the board model and firmware commit.

### B. OLED test

1. Connect one OLED to GPIO21/GPIO22 only.
2. Scan and record its I2C address.
3. Display node ID, firmware version, and a test message.
4. Repeat for the second OLED.
5. Confirm the display does not reset the ESP32.

### C. Keypad/input test

1. Identify whether the keypad is 3×4, 4×4, or another matrix.
2. Record row and column pins before wiring.
3. Test one key/input at a time.
4. Confirm that a key press produces one serial event after debouncing.
5. Do not connect keypad pins that conflict with the LoRa SPI or OLED I2C map.

### D. Radio initialization test

1. Verify both radio module markings and antenna frequency.
2. Wire each radio using the verified `docs/pin_map.md`.
3. Connect antennas before any transmission.
4. Power over USB first.
5. Confirm both radios initialize successfully.
6. Record the final frequency, bandwidth, spreading factor, coding rate, CRC, and transmit power.

### E. HELLO discovery test

1. Power Node 1 and Node 2.
2. Confirm periodic HELLO events on both serial monitors.
3. Confirm Node 2 records Node 1 as a fresh neighbor.
4. Confirm Node 2 advertises a connected or usable route state.
5. Save both serial logs.

### F. REPORT and ACK test

1. Send `r` through Node 2’s serial monitor.
2. Confirm Node 1 receives the report.
3. Confirm Node 1 sends an ACK.
4. Confirm Node 2 emits `ACKED` for the matching origin and sequence.
5. Repeat at least 20 times.
6. Record delivery, latency, retry count, and failures.

### G. Retry test

1. Start with both nodes close together.
2. Interrupt or obstruct the link in a controlled manner without damaging the hardware.
3. Generate one report.
4. Confirm retry telemetry appears after the configured ACK timeout.
5. Confirm the report is removed after the retry limit is exhausted.
6. Restore the link and verify a new report succeeds.

### H. Neighbor-expiry test

1. Confirm Node 2 has learned Node 1.
2. Power down Node 1.
3. Wait longer than `kNeighborExpiryMs`.
4. Confirm Node 2 removes or invalidates the stale neighbor.
5. Generate a report from Node 2.
6. Confirm it records `NO_ROUTE` instead of using stale neighbor data.
7. Power Node 1 back on.
8. Confirm a fresh HELLO restores route eligibility.

## Evidence to save

```text
two_node_pair_test/
├── node_1_serial.log
├── node_2_serial.log
├── firmware_commit.txt
├── board_and_radio_models.txt
├── final_pin_map.txt
├── radio_configuration.txt
├── oled_addresses.txt
├── keypad_pin_map.txt
├── experiment_metadata.json
└── wiring_photos/
```

## Acceptance criteria

The pair milestone passes only when:

- Both ESP32 boards boot reliably.
- Both radios initialize reliably with antennas attached.
- HELLO packets create and refresh neighbor records.
- A report reaches the base station.
- A matching ACK clears the pending report.
- Retry and exhaustion behavior is visible in serial logs.
- Neighbor expiry prevents use of a stale route.
- OLED and keypad events agree with serial telemetry.
- The complete test can be reproduced from the saved commit and configuration.
