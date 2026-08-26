# Sahayak v2.0 Hardware Baseline and Procurement Checklist

## Frozen first revision

The first revision uses a modular ESP32 plus an explicitly verified 868 MHz-class LoRa radio. The team should use the same board and module model across all nodes wherever possible.

> **Do not purchase a generic “SX1278 LoRa module” without checking its frequency marking. A 433 MHz module is not suitable for the intended 868 MHz design.**

## Core node quantities

The recommended initial purchase supports eight complete nodes: one base station, two relay nodes, four field/human-relay nodes, and one spare/test node. If the budget requires staged procurement, purchase two complete nodes first, then expand to five and eight nodes after the direct link works.

| Component | Baseline specification | Initial quantity | Status |
|---|---|---:|---|
| ESP32 development board | ESP32-WROOM-32 / ESP32 DevKit-class, USB programmable | 8 + 1 spare if possible | To confirm exact model |
| LoRa radio | 868 MHz SX1276-class, SPI interface; RFM95W 868 MHz or equivalent | 8 + 1 spare if possible | **Frequency must be verified** |
| Antenna | Matched 868 MHz antenna with correct SMA/u.FL connector | 8 + 2 spares | Must match radio connector |
| OLED | 0.96-inch SSD1306, I2C, 128×64 | 8 | Confirm I2C address |
| Emergency button | Large momentary normally-open button | 8 | Active-low firmware configuration |
| Operator/ACK button | Momentary button | 4–8 | Required for base/human-relay nodes first |
| LEDs | Red, green, yellow/blue | 24–32 total | One resistor per LED |
| LED resistors | 220–330 ohm | 24–32 | One per LED |
| Buzzer | Small 3.3 V active buzzer | 8 | Use transistor driver if needed |
| Buzzer driver | 2N2222/BC547 plus base resistor | 8 sets | Protects ESP32 GPIO |
| Decoupling capacitors | 100 nF plus 10 µF near radio/power rail | 8 sets | Helps with transmit bursts |
| Headers/connectors | 2.54 mm headers, JST/screw terminals | Assorted | Prefer replaceable wiring |

## Power baseline

Use stable USB power for the first two-node and three-node firmware milestones. Add batteries only after radio communication, logging, and forwarding work.

| Component | Baseline specification | Quantity | Notes |
|---|---|---:|---|
| Bench power | USB power bank or regulated 5 V supply | 4–8 | First bring-up power source |
| Field battery | Protected 1-cell Li-ion 18650 or protected 3.7 V LiPo, approximately 2000–3000 mAh | 8 | Do not use loose unprotected cells |
| Charger/protection | Reputable 1-cell charger with protection | 8 or shared | Must match the chosen battery |
| Regulator | 3.3 V regulator/buck-boost sized for ESP32 and LoRa peaks | 8 | Confirm after exact boards are selected |
| Power switch | Slide or latching switch | 8 | Required for failure tests |
| Battery connector | Locking JST or equivalent | 8 | Prevents loose wiring |

## Measurement and test equipment

| Equipment | Suggested quantity | Purpose |
|---|---:|---|
| INA219 or equivalent current monitor | 3–8 | Current/voltage measurement during transmit, receive, idle, and sleep |
| Laptop | 1 | Base station and experiment control |
| Raspberry Pi-class computer | 0–1 | Optional field gateway |
| USB cables | 8–10 | Programming and serial logs |
| Multimeters | 2 if possible | Debugging and power checks |
| USB power meters | 1–2 | Quick power checks |
| GPS or smartphone location logging | 1 shared | Node positions and field-test records |

## Mechanical materials

- Breadboards for bench prototypes.
- Perfboards or custom PCBs after the pin map is frozen.
- IP65 plastic enclosures for controlled outdoor tests.
- Cable glands and rubber grommets.
- Nylon standoffs, screws, and heat-shrink tubing.
- Soldering, crimping, and continuity-test tools.

## Purchase verification checklist

Before accepting any radio module order, record:

- [ ] Exact manufacturer and module part number.
- [ ] Frequency marking: 868 MHz or explicit compatibility with the selected Indian operating band.
- [ ] Radio chip: SX1276-class or equivalent approved choice.
- [ ] Interface: SPI or another interface deliberately supported by the firmware.
- [ ] Operating voltage and logic-level requirements.
- [ ] Maximum transmit power and antenna connector.
- [ ] Board schematic or trustworthy datasheet.
- [ ] Quantity and spare modules.

Before flashing all nodes, record:

- [ ] Exact ESP32 board revision.
- [ ] Final GPIO map.
- [ ] OLED I2C address.
- [ ] Battery-divider ratio, if used.
- [ ] Radio frequency and LoRa parameters.
- [ ] Node ID assigned to each physical board.
