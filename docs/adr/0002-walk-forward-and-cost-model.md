# ADR 0002: Walk-forward evaluation and explicit transaction costs

## Status

Accepted

## Context

The initial backtest assumed frictionless fills and a single in-sample run. Production quant research separates **planning**, **simulation**, and **risk** — and reports metrics on out-of-sample folds with realistic costs.

Upstream references:

- **backtesting.py** models commission and spread at the broker layer.
- **vectorbt** encourages split/rolling evaluation rather than one aggregate curve.
- **LangGraph** treats each pipeline stage as an explicit node with a typed handoff.

## Decision

1. Add `CostAssumptions` (commission + slippage in basis points) applied on position changes.
2. Add walk-forward evaluation over contiguous folds with aggregated fold metrics.
3. Export `ResearchPlan.to_artifact()` as the structured contract between planner and simulator.

## Consequences

- Reports include `cost_drag` and `walk_forward` summaries for auditability.
- Research-only boundary preserved — no broker or live execution hooks.
- Full vectorbt / FinRL engines remain future adapters behind the same interfaces.
