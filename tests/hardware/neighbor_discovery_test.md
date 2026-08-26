# Hardware Test: Neighbor Discovery and Route Expiry

## Objective

Verify that a node learns a neighbor from periodic `HELLO` packets, records link metrics, advertises route health, and removes the neighbor after the freshness timeout.

## Required setup

- Two or three identical ESP32–LoRa nodes.
- Matched antennas.
- USB serial connections for all nodes.
- One base station and at least one relay/field node.
- A firmware commit containing the neighbor manager.

## Procedure

1. Flash the nodes with unique IDs and configure the intended static next hops.
2. Power the base station and relay/field node with USB power.
3. Confirm that each node emits periodic `HELLO` records.
4. Confirm that the receiving node reports the sender ID, RSSI, SNR, neighbor count, and current route-health state.
5. Stop the sender node’s power or move it outside the controlled test range.
6. Wait longer than the configured `kNeighborExpiryMs` value.
7. Confirm that the receiver no longer treats the sender as fresh.
8. Confirm that a generated report produces `NO_ROUTE` when the configured next hop has expired.
9. Restore the sender and confirm that a new HELLO returns the receiver to a usable state.

## Acceptance criteria

- A valid HELLO creates one neighbor record.
- Repeated HELLO packets update the same record rather than creating duplicates.
- RSSI and SNR are retained from the latest HELLO.
- The neighbor expires after the configured timeout.
- The node does not transmit a report through an expired configured next hop.
- A fresh HELLO restores route eligibility.
- Serial logs contain the firmware commit and complete event sequence.

## Evidence

Save the two serial logs, the node-ID configuration, the radio configuration, the physical placement, the exact expiry constant, and the firmware commit hash.
