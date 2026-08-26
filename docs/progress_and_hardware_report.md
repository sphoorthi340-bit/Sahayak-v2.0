# Sahayak v2.0 Progress and Hardware Action Report

**Project role:** Embedded Systems and Adaptive Routing Lead  
**Current development mode:** Software-first, with a two-node hardware pair now available  
**Repository:** [sphoorthi340-bit/Sahayak-v2.0](https://github.com/sphoorthi340-bit/Sahayak-v2.0)  
**Report purpose:** Provide one document that can be read and followed without needing another project explanation.

## 1. Executive assessment

Sahayak v2.0 has progressed beyond a simple idea or classroom prototype. The repository now contains a coherent packet protocol, ESP32–LoRa firmware foundation, neighbor discovery, route expiry, dynamic routing, route hysteresis, hop-by-hop ACK/retry logic, base-station logging, topology analysis, priority triage, human-relay semantics, deterministic simulation, and automated tests.

The most important boundary is that the software is ahead of the physical evidence. The code can compile and the logic can be tested in simulation, but the project cannot yet claim real LoRa packet-delivery performance, terrain robustness, energy consumption, or paper-ready field validation. The two ESP32 boards, two OLEDs, two keypads, and other pair materials are enough to begin a meaningful two-node bench prototype immediately.

## 2. Current progress

| Area | Current status | Interpretation |
|---|---:|---|
| Repository structure and documentation | 95% | Organized and usable as the project source of truth |
| Packet protocol and serialization | 85% | Core fields and validation exist; later extensions remain |
| Two-node firmware foundation | 75% software-side | Compiled and logically tested; needs physical flashing |
| Neighbor discovery and route expiry | 80% software-side | HELLO processing and stale-neighbor removal exist |
| Dynamic routing | 75% software-side | RSSI, advertised hop count, and queue-length selection exist |
| Route hysteresis | 70% software-side | Stable-route margin exists; real route churn must be measured |
| ACK/retry reliability | 70% software-side | Pending ACKs, bounded retries, timeout telemetry exist |
| Base-station logging and metrics | 80% | Serial parsing, SQLite logging, topology, and metrics exist |
| Priority and fairness behavior | 70% software-side | FIFO, priority, and aging-queue tools exist |
| Human-relay semantics | 60% software-side | Corroboration/rejection/escalation model exists; radio command path remains |
| Physical hardware validation | 0% completed | Pair testing can now begin |
| Five-to-eight-node field validation | 0% completed | Requires additional nodes and controlled deployment |
| Paper-ready experimental evidence | Approximately 20–30% | Real measurements are still required |

The practical interpretation is that the **software prototype is approximately 65–70% complete**, while the **full research system is approximately 40–50% complete**. The difference is caused by the missing hardware measurements, not by a lack of software structure.

## 3. How much software remains

The remaining software work is substantial but manageable. Approximately 25–35% of the planned software remains, depending on how polished the final system must be.

| Remaining software area | Estimated remaining work | Can be completed without full hardware? |
|---|---:|---|
| Route advertisement refinement and path validity | Medium | Mostly yes |
| End-to-end ACK path reversal | Medium | Mostly yes, with simulation first |
| Retry calibration and radio-specific timeout tuning | Medium | Logic yes; final values require hardware |
| OLED interface driver and status screens | Medium | Yes, once the exact OLED is confirmed |
| Keypad driver and emergency-report menu | Medium | Yes, once keypad type/pin map is confirmed |
| Human-relay command packets and operator workflow | Medium | Protocol and simulator yes; radio confirmation later |
| Base-station live dashboard | Low–medium | Yes |
| Experiment controller and report export | Medium | Yes, using logs and scenario files |
| Security/authentication extension | Medium | Yes, but should follow core validation |
| Battery/current telemetry integration | Medium | Software yes; calibration requires hardware |
| Hardware-dependent route and energy tuning | High | No; requires physical nodes |
| Final paper tables and claims | High | No; requires real experimental logs |

I can complete most of the code, documentation, simulation, tests, experiment scripts, log analysis, and paper structure. You must perform the physical actions that cannot be done remotely: identify the exact boards, wire them, connect antennas, flash firmware, operate keypads, move or power-cycle nodes, observe the OLEDs, collect serial logs, and record field conditions.

## 4. What the current pair can prove

Two complete radio nodes can provide valuable evidence, but they cannot prove the entire research claim.

### The pair can test

- ESP32 programming and boot behavior.
- LoRa initialization.
- Correct frequency and radio configuration.
- Direct `HELLO` exchange.
- Direct `REPORT` delivery.
- ACK generation and matching.
- Retry and timeout behavior.
- RSSI and SNR logging.
- Direct-link packet delivery ratio.
- Direct-link latency.
- Duplicate suppression at the software level.
- Route expiry by powering off one node.
- OLED status behavior after the UI driver is integrated.
- Keypad-driven report generation after the keypad driver is integrated.
- Base-station serial logging and SQLite storage.
- Repeatability of a controlled two-node experiment.

### The pair cannot yet test

- A true three-node relay path.
- Alternative-path selection.
- Independent-path redundancy.
- Cascading relay failure.
- Five-to-eight-node scalability.
- Human-relay behavior involving a separate relay node.
- Terrain-constrained multihop performance.
- Network-wide queue congestion.

Therefore, the pair is not a wasted partial setup. It is the correct first experimental stage and will expose wiring, frequency, packet, timeout, and power problems before the team invests in a larger testbed.

## 5. Exact two-node roles

Use the two nodes as follows:

| Physical node | Node ID | Role |
|---|---:|---|
| Node A | 1 | Base station / receiver / ACK generator |
| Node B | 2 | Field node / report generator / retry client |

The repository’s current firmware configuration uses `kNodeId` as a compile-time setting. Flash the same source twice, changing only the node ID. Do not create separate codebases for the two boards.

If the two “other materials” include two compatible 868 MHz LoRa radios and two matched antennas, the pair can begin RF testing. If they include only the ESP32, OLED, and keypads but no LoRa radios and antennas, begin with UI and protocol work but do not attempt RF transmission.

## 6. Hardware preparation when you are ready

### Step 0: inventory before powering

Make a simple record of every part. Photograph the front and back of both ESP32 boards and both LoRa modules. Record the exact model marking on each radio, the antenna connector type, the OLED controller marking, and the keypad type.

The minimum RF pair is:

| Item | Quantity needed |
|---|---:|
| ESP32 DevKit-class board | 2 |
| Explicitly verified 868 MHz SX1276-class LoRa module | 2 |
| Matched 868 MHz antennas | 2 |
| Stable USB power source | 2 |
| USB programming cables | 2 |
| OLED modules | 2, optional for the first RF test |
| Keypads | 2, optional for the first RF test |

Do not transmit from a radio without its antenna connected. Do not assume that a bare radio module is 5 V tolerant. Verify the module’s power and logic requirements from its own documentation.

### Step 1: verify the wiring map

The repository contains a provisional map in [`docs/pin_map.md`](pin_map.md). The initial example is:

| Function | ESP32 GPIO |
|---|---:|
| LoRa SCK | 18 |
| LoRa MISO | 19 |
| LoRa MOSI | 23 |
| LoRa NSS/CS | 5 |
| LoRa RESET | 14 |
| LoRa DIO0 | 26 |
| OLED SDA | 21 |
| OLED SCL | 22 |
| Emergency input | 27 |
| Operator input | 33 |
| Green LED | 25 |
| Red LED | 32 |
| Buzzer | 13 |
| Battery ADC | 34 |

This is not permission to wire blindly. Compare it with the exact purchased boards, ensure a common ground, check for shorts, and update the repository if the hardware differs.

### Step 2: first power test

Power each ESP32 over USB without the LoRa module attached. Confirm that each board can be detected and programmed. Confirm serial output at 115200 baud. If a board resets repeatedly, stop and solve the power or USB issue before adding the radio.

### Step 3: attach the radio safely

Wire the LoRa module using the verified map. Connect the matched antenna before the first radio initialization/transmission test. Keep the radio supply stable and place local decoupling near the radio power pins.

### Step 4: assign node IDs

For Node A, set:

```cpp
constexpr uint8_t kNodeId = 1;
```

Flash and test it. For Node B, set:

```cpp
constexpr uint8_t kNodeId = 2;
```

Flash and test it. Keep `kBaseStationId = 1` on both nodes. Commit or record the exact firmware revision used.

### Step 5: use conservative radio settings

The repository currently uses a provisional 866.5 MHz test frequency, 125 kHz bandwidth, spreading factor 7, coding rate 4/5, CRC enabled, and conservative 14 dBm transmit power. These values must be checked against the exact radio, antenna, and applicable local rules before outdoor RF testing.

Do not modify the frequency or power independently on one node. Both nodes in one experiment must use identical radio settings.

## 7. First two-node test sequence

Run the first test without the OLED and keypad if necessary. The aim is to prove the radio path before adding UI complexity.

1. Flash Node A with ID 1 and Node B with ID 2.
2. Open a serial monitor for each board.
3. Confirm both boards boot and initialize the radio.
4. Confirm both nodes emit periodic `HELLO` events.
5. Confirm Node B learns Node A as a fresh neighbor.
6. Confirm Node B changes from `DISCOVER_NEIGHBORS` to `CONNECTED` when a valid route is available.
7. Press `h` in the Node B serial monitor to send a HELLO manually.
8. Press `r` in the Node B serial monitor to send a test report.
9. Confirm Node A receives the report.
10. Confirm Node A emits an ACK.
11. Confirm Node B logs the matching ACK and clears the pending transmission.
12. Save both serial logs, firmware commit, hardware record, and radio configuration.

The first milestone is successful only when the event sequence can be reconstructed from the saved logs. A blinking LED or an OLED message without a serial record is not sufficient evidence.

## 8. Two-node experiment matrix

Run these experiments in order. Do not jump directly to distance or terrain testing.

| Test | Change one variable | Main measurements | Pass condition |
|---|---|---|---|
| Boot test | None | Boot time, reset behavior | Both nodes remain stable |
| HELLO test | Periodic discovery | HELLO count, neighbor state | Neighbor is learned |
| REPORT/ACK test | One report at a time | Delivery, ACK, latency | Matching ACK clears pending state |
| Repetition test | 50–100 reports | PDR, latency, retries | Logs contain every outcome |
| Distance test | Increase separation | RSSI, SNR, PDR | Measurements are repeatable |
| Retry test | Temporarily obstruct or separate nodes | Retry count, timeout | Exhaustion is logged explicitly |
| Expiry test | Power off Node A | Last HELLO, expiry time | Node B refuses stale route |
| Recovery test | Power Node A back on | Re-learning time | Node B becomes connected again |
| OLED test | Add display | State and metrics | Display agrees with serial log |
| Keypad test | Add keypad input | Generated report fields | Correct report is logged |

Use the same packet count, radio settings, node positions, and firmware commit when comparing configurations.

## 9. How to use the OLEDs and keypads

The current radio and protocol foundation is the priority. The OLED and keypad are application-layer additions. The current provisional pin map reserves I2C pins 21/22 for the OLED, emergency input 27, and operator input 33, but the exact keypad matrix wiring is not yet frozen.

Once the radio pair works, add the peripherals one at a time:

1. Scan and record the OLED I2C address.
2. Display node ID and current route state.
3. Display neighbor count, next hop, RSSI, SNR, queue length, and retry count.
4. Test one keypad key or emergency input before connecting the entire matrix.
5. Add the keypad driver after confirming whether the keypad is 3×4, 4×4, or another matrix.
6. Map keypad actions to severity, people affected, trapped persons, region, and report submission.
7. Compare the OLED and keypad event with the serialized report stored at the base station.

Do not let the keypad UI delay the first radio test. Serial commands are sufficient for the first communication milestone.

## 10. What to save for every test

For every test run, save:

```text
firmware_commit.txt
hardware_record.txt
radio_configuration.txt
node_a_serial.log
node_b_serial.log
experiment_metadata.json
photos/
```

The metadata should contain:

```text
experiment_id
start_time
end_time
node_ids
firmware_commit
radio_module_models
frequency
bandwidth
spreading_factor
coding_rate
transmit_power
antenna_type
power_source
node_positions
separation_meters
environment
weather_if_outdoors
packet_count
traffic_pattern
failure_event
operator_notes
```

Never rely on memory after a test. The paper will need reproducible evidence, not only a successful demonstration.

## 11. What happens when the full hardware arrives

When more nodes are available, replicate the proven pair design rather than modifying every node independently.

### Expansion order

1. Two-node direct link: source and base.
2. Three-node line: field node, relay, base.
3. Three-node alternative paths: field node with two possible relays.
4. Five-node controlled mesh.
5. Eight-node mixed-role network.
6. Mixed-terrain deployment.

### Node-role assignment

| Node IDs | Suggested role |
|---|---|
| 1 | Base station |
| 2–3 | Relay nodes |
| 4–6 | Field nodes |
| 7 | Human-relay/operator node |
| 8 | Spare/test node |

### Full hardware workflow

For every additional node, repeat the inventory, wiring, antenna, programming, and self-test process. Assign a unique node ID, record the hardware revision, and confirm that all nodes use the same radio configuration.

First verify that all nodes hear HELLO messages. Then verify three-node forwarding. Then add alternate paths and compare routing modes. Only after the network is stable should you run controlled node failures, surge traffic, battery tests, and terrain deployments.

## 12. Paper evidence plan

The paper should not use simulation outputs as if they were field measurements. Use the software simulations to debug and select scenarios. Use the physical logs to support claims.

The final evidence should include:

| Research claim | Required evidence |
|---|---|
| Adaptive routing improves delivery | Same scenarios under RSSI-only and adaptive routing |
| Adaptive routing reduces congestion | Queue length, waiting time, and retry logs |
| Risk warnings are proactive | Warning timestamp before controlled failure or path loss |
| Human relay adds value | Automated-only versus human-assisted comparison |
| System works in terrain | Controlled placement and mixed-terrain measurements |
| System is energy-aware | Current/voltage logs by radio state and delivered packet |
| System is reproducible | Firmware commit, configuration, placement, and raw logs |

## 13. Troubleshooting order

When a physical test fails, check in this order:

1. Antenna connected and matched.
2. Radio frequency marking and configuration.
3. Radio supply voltage and current capability.
4. Common ground.
5. SPI wiring.
6. CS, reset, and DIO0 pins.
7. Unique node IDs.
8. Serial baud and logs.
9. Identical bandwidth, spreading factor, coding rate, CRC, and power settings.
10. Only then investigate routing logic.

A node that resets during transmission is usually a power or wiring problem before it is a routing problem. A node that receives nothing may have a frequency, antenna, SPI, or interrupt issue before it has a protocol problem.

## 14. Immediate action list

For your current pair, the correct order is:

1. Confirm whether the “other materials” include two 868 MHz LoRa modules and two matched antennas.
2. Record exact model numbers and take clear photographs.
3. Verify the provisional pin map against the boards.
4. Build only Node A and Node B.
5. Flash IDs 1 and 2.
6. Run the serial-only HELLO/REPORT/ACK test.
7. Save the logs and hardware record.
8. Add OLEDs one at a time.
9. Add keypads one at a time.
10. Use the resulting pair evidence to correct the firmware before ordering or assembling the larger testbed.

## 15. Project conclusion

You are not starting late or with too little hardware. Two nodes are the correct minimum to convert the software foundation into measured evidence. They can validate the first communication, discovery, route-health, ACK/retry, display, keypad, and logging path. They cannot validate the final mesh novelty claim, so the report must keep the pair milestone separate from the later relay and field milestones.

The repository is ready for the two-node stage. Your physical role is to assemble, flash, observe, and log. My role is to continue implementing the firmware, protocol, base-station, simulations, test automation, analysis, documentation, and paper structure around the evidence you collect.

## Project references

- [Main repository README](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/README.md)
- [Packet protocol](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/docs/protocol.md)
- [Pin map](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/docs/pin_map.md)
- [Hardware bill of materials](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/hardware/bom.md)
- [Hardware bring-up checklist](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/hardware/bringup_checklist.md)
- [Dynamic routing specification](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/docs/dynamic_routing.md)
- [Reliability specification](https://github.com/sphoorthi340-bit/Sahayak-v2.0/blob/main/docs/reliability.md)
- [Hardware test area](https://github.com/sphoorthi340-bit/Sahayak-v2.0/tree/main/tests/hardware)
