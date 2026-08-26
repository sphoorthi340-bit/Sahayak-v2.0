from base_station.metrics import summarize_events
from base_station.packet_parser import parse_event


def test_summary_metrics():
    lines = [
        "EVENT,t_ms=100,node=2,type=REPORT,origin=2,seq=10,prev=255,next=1,hop=0,ttl=8,rssi=0,snr=0,queue=0,retry=1,state=CONNECTED,outcome=CREATED",
        "EVENT,t_ms=130,node=1,type=REPORT,origin=2,seq=10,prev=2,next=1,hop=1,ttl=7,rssi=-90,snr=6.0,queue=0,retry=0,state=CONNECTED,outcome=DELIVERED",
        "EVENT,t_ms=140,node=1,type=REPORT,origin=2,seq=10,prev=2,next=1,hop=1,ttl=7,rssi=-90,snr=6.0,queue=0,retry=0,state=CONNECTED,outcome=DUPLICATE",
    ]
    events = [parse_event(line) for line in lines]
    summary = summarize_events([event for event in events if event is not None])
    assert summary.created == 1
    assert summary.delivered == 1
    assert summary.packet_delivery_ratio == 1.0
    assert summary.median_latency_ms == 30.0
    assert summary.total_retries == 1
    assert summary.duplicates == 1
