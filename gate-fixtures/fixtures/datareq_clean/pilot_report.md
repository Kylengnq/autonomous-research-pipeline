# Pilot report: K3-1

Verdict: construction-open. Usable sample 80 units / 14 meetings.

```data_request
status: required
quantity: effective half-spread at the release instant
why_it_matters: separates the liquidity channel from the information channel; without it the coefficient is a composite of both and the paper cannot name a mechanism
candidates:
  - source: TAQ millisecond quotes
    route: purchasable
    join_key: ticker x date
    probe: unprobed: no licence to sample against before purchase
    cost_time: ~$1.5k, 2 weeks procurement
  - source: paired YES/NO contract prices in the held extract
    route: held
    join_key: market_id x timestamp
    probe: 94.2% match on a 5,000-row slice (scripts/probe_paired.py)
    cost_time: none, already held
fallback: YES/NO no-arbitrage bound from paired contract prices
```
