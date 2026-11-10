# Pilot report: K3-1

Verdict: construction-open. Usable sample 80 units / 14 meetings.

```data_request
status: required
quantity: the level-2 quote stack table from the vendor feed
why_it_matters: we need the spread
candidates:
  - source: TAQ millisecond quotes
    route: purchasable
    join_key: ticker x date
    probe: unprobed: no licence yet
    cost_time: ~$1.5k
fallback: none available
```
