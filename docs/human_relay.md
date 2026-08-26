# Human-Relay Protocol Layer

## Purpose

A human relay is treated as a protocol participant rather than only a user-interface endpoint. The software layer represents an operator’s assessment of an emergency report and preserves the decision for later analysis.

## Relay actions

| Action | Meaning | Priority effect |
|---|---|---|
| `PENDING` | Report is awaiting human assessment | Original severity is retained |
| `CORROBORATED` | Human relay confirms the report | Escalates to emergency priority 3 |
| `REJECTED` | Human relay finds the report unconfirmed or incorrect | Reduces priority to routine/low |
| `ESCALATED` | Human relay forwards the report for immediate attention | Escalates to emergency priority 3 |

Every decision records the relay node ID and an optional operator note. The note should explain the basis of the decision without including sensitive personal information.

## Current software implementation

`base_station/human_relay.py` provides an auditable state manager. It deduplicates reports by `(origin_id, sequence)`, records the human decision, produces an effective priority, and returns a deterministic priority order for the base-station queue.

This makes it possible to compare:

1. Automated priority only.
2. Automated priority plus human corroboration.
3. Automated priority plus human rejection or escalation.

## Future packet extension

The `COMMAND` message type is reserved for transmitting relay decisions over LoRa. A future command payload should include the report origin, sequence, relay ID, action, decision timestamp, and bounded note/code. The current base-station module is intentionally implemented first so the semantics are stable before adding another radio payload.

## Research boundary

The human-relay contribution is not simply the existence of an OLED or button. It must be evaluated as a change in report handling, queue priority, delivery time, and false-alert management. The paper should report human-assisted and automated-only scenarios separately.
