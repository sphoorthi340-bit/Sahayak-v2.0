# Sahayak Base Station

The base station receives machine-readable telemetry from the gateway ESP32 over USB serial. The first milestone is intentionally command-line based: reliable parsing and logging are more important than a dashboard.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run with a real serial port

```bash
python3 -m base_station.main --serial-port /dev/ttyUSB0 --baud 115200 --database experiments/raw_logs/sahayak.sqlite
```

## Run with saved or piped input

```bash
printf '%s\n' 'EVENT,t_ms=10,node=2,type=HELLO,origin=2,seq=1,prev=255,next=255,hop=0,ttl=8,rssi=0,snr=0,queue=0,retry=0,state=CONNECTED,outcome=FORWARDED' | python3 -m base_station.main --database /tmp/sahayak-demo.sqlite
```

## Current scope

The base-station milestone supports event parsing and durable SQLite logging. Topology analysis, priority triage, failure-risk assessment, experiment control, and plots are added in later milestones.
