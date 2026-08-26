# Sahayak Test Area

This directory contains project-level validation that is not tied to one Python module or one firmware source file.

## Test categories

| Directory | Purpose | Hardware required |
|---|---|---|
| `software/` | Protocol, routing, topology, queue, and metrics tests | No |
| `simulation/` | Repeatable network scenarios and routing comparisons | No |
| `hardware/` | Physical node, radio, power, antenna, and field tests | Yes |
| `fixtures/` | Small deterministic logs and packet examples | No |

The existing `base_station/tests/` directory contains unit tests for the Python package. New cross-component or scenario-level tests should be placed here.

## Rule for hardware tests

Hardware tests must record the exact board, radio module, antenna, firmware commit, radio settings, node placement, power source, and environmental conditions. Do not treat a failed physical test as a software failure until power, antenna, wiring, frequency, and serial logs have been checked.

## Current status

The hardware test files are placeholders until the components arrive. Software and simulation tests can be developed now.
