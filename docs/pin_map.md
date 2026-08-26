# Sahayak Provisional Pin Map

This pin map is for the first ESP32 DevKit-class prototype. It must be verified against the exact ESP32 board, LoRa breakout, OLED board, and wiring before soldering the complete node set.

| Function | Example GPIO | Direction | Notes |
|---|---:|---|---|
| LoRa SCK | GPIO18 | Output | VSPI clock example |
| LoRa MISO | GPIO19 | Input | VSPI data example |
| LoRa MOSI | GPIO23 | Output | VSPI data example |
| LoRa NSS/CS | GPIO5 | Output | Radio chip select |
| LoRa RESET | GPIO14 | Output | Radio reset |
| LoRa DIO0 | GPIO26 | Input | Radio interrupt for packet events |
| OLED SDA | GPIO21 | Bidirectional | I2C data |
| OLED SCL | GPIO22 | Output | I2C clock |
| Emergency button | GPIO27 | Input pull-up | Active-low, software debounce |
| Operator/ACK button | GPIO33 | Input pull-up | Optional on relay/base nodes |
| Green LED | GPIO25 | Output | Connected/ACK state |
| Red LED | GPIO32 | Output | Emergency/risk state |
| Buzzer control | GPIO13 | Output | Use a transistor if required by the buzzer load |
| Battery ADC | GPIO34 | Input | Must use a resistor divider and verify ADC range |

## Wiring rules

The selected radio module must be powered according to its own schematic. Do not assume that a bare radio module is 5 V tolerant. If the breakout includes a regulator and level shifting, verify those features in the manufacturer documentation.

Keep the RF path short and mechanically secure. Always connect the matched antenna before transmitting. Use common ground between the ESP32, radio, OLED, and other peripherals. Place local decoupling capacitors near the radio and power input.

Do not use a GPIO configuration that holds an ESP32 boot-strapping pin at the wrong logic level during reset. If the selected board conflicts with this provisional map, update this document and the firmware configuration together.

## Pin-map verification checklist

- [ ] Exact ESP32 board model recorded.
- [ ] Exact radio module model and frequency recorded.
- [ ] Radio power and logic voltage verified.
- [ ] Antenna connector and antenna frequency verified.
- [ ] OLED I2C address scanned.
- [ ] Buttons tested with pull-up and debounce.
- [ ] LED current-limiting resistors installed.
- [ ] Buzzer driver requirement checked.
- [ ] Battery-divider ratio calculated and tested.
- [ ] All GPIO conflicts checked before replication.
