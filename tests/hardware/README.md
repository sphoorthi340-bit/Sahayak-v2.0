# Hardware Test Placeholders

These tests will be completed after the ESP32 and LoRa components arrive.

## Planned tests

1. ESP32 programming and serial-output test.
2. Radio initialization test.
3. Antenna and frequency verification.
4. Two-node HELLO exchange.
5. Two-node REPORT and ACK exchange.
6. RSSI/SNR range test.
7. Three-node forwarding test.
8. Retry and packet-loss test.
9. Power and brownout test.
10. Battery/current measurement test.
11. Outdoor mixed-terrain test.
12. Controlled relay-failure test.

Each test should eventually have a file containing:

```text
purpose:
required_nodes:
required_equipment:
firmware_commit:
hardware_revision:
radio_configuration:
procedure:
expected_result:
observed_result:
raw_log_path:
pass_or_fail:
notes:
```

## Do not run yet

Do not transmit from unverified hardware or use an unverified antenna. Do not perform outdoor experiments until the team has confirmed the exact radio module, frequency, antenna, power source, and enclosure condition.
