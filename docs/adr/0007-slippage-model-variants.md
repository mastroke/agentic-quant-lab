# ADR 0007: Pluggable slippage model variants

## Status

Accepted

## Context

ADR 0002 introduced a single fixed slippage rate in basis points bundled with commission. Realistic research needs distinct friction shapes: constant per-trade drag, size-dependent market impact, and quoted spread costs.

## Decision

1. Add `SlippageModel` protocol with three dataclass implementations:
   - `FixedSlippage` — constant bps per unit position change
   - `ProportionalSlippage` — bps scaled by trade magnitude
   - `SpreadBasedSlippage` — half- or full-spread cost with optional per-bar override
2. Extend `CostAssumptions` with optional `slippage_model`; legacy `slippage_bps` remains the default fixed model.
3. Route MA and buy-and-hold simulators through `trade_cost()` / `compute_trade_costs()` so commission and slippage compose per bar.

## Consequences

- Existing plans and tests that only set `slippage_bps` behave unchanged.
- Price frames may supply a `spread_bps` column for bar-level spread assumptions.
- Future adapters (vectorbt, broker feeds) can plug in custom `SlippageModel` implementations without touching simulators.
