# Sahayak Hardware Integration Notes

## First prototype target

Build two identical USB-powered nodes first. Each node should contain:

- ESP32 DevKit-class board.
- Explicitly verified 868 MHz-class SX1276 LoRa module.
- Matched 868 MHz antenna.
- Stable USB power.
- Optional OLED, emergency button, status LEDs, and buzzer after the radio link is stable.

The current firmware assumes the provisional pin map in [`docs/pin_map.md`](../docs/pin_map.md). Confirm the exact board model before replication.

## Build order

1. Verify the radio module frequency and antenna connector.
2. Test ESP32 USB programming without the radio attached.
3. Wire the radio and verify power/ground continuity.
4. Flash the radio initialization firmware.
5. Test two-node `HELLO` exchange.
6. Add the OLED and user inputs.
7. Add battery and current measurement only after USB tests pass.
8. Move from breadboard to perfboard or a PCB after the pin map is frozen.

## Physical safety

Never transmit without the correct antenna connected. Do not use an unprotected lithium cell in a field node. Test the power regulator under transmit load and watch for ESP32 brownouts. Do not place a breadboard prototype outdoors without protection from moisture and accidental shorts.

## Hardware records

For every node, record:

```text
node_id:
esp32_board:
radio_module:
radio_frequency:
antenna_type:
power_source:
regulator:
oled_address:
firmware_commit:
notes:
```
