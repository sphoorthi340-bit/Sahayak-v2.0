# Priority and Queue Experiments

## Objective

Measure whether emergency reports receive lower waiting time and higher service priority during report surges, while routine traffic continues to make progress.

## Comparison modes

The experiment should compare at least:

| Mode | Queue policy |
|---|---|
| FIFO | Serve reports in arrival order |
| Priority | Serve the highest-priority available report first, FIFO within equal priority |
| Priority with fairness | Serve high-priority reports first while applying a bounded waiting-age boost to prevent starvation |

The current software runner implements FIFO and priority modes. The fairness refinement should be added before final field experiments if the priority queue can starve routine traffic.

## Required metrics

For each priority class, record:

- Number of reports generated.
- Number served.
- Mean waiting time.
- Median waiting time.
- 95th-percentile waiting time.
- Service completion time.
- Drop or overflow count.
- Priority inversion count.
- Maximum waiting time for routine reports.

## Reproducibility rules

The scenario file must remain fixed while comparing queue policies. Keep report arrival times, priorities, service duration, packet payload size, radio settings, node placement, and failure events unchanged. Only the queue policy should change.

The current deterministic scenario is `experiments/scenarios/priority_surge.json`. Run it with:

```bash
PYTHONPATH=. python3 experiments/priority_surge.py \
  experiments/scenarios/priority_surge.json \
  --output experiments/processed_results/priority_surge.csv
```

The output is software validation only. Real queue waiting time must later be measured from firmware and base-station event logs under controlled packet surges.
