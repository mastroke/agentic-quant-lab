# ADR 0005: Benchmark-relative reporting

## Status

Accepted

## Context

Absolute return and drawdown on a strategy are hard to interpret without a passive baseline. Research reviews need to know whether a rule adds value over simply holding the underlying asset.

## Decision

1. Add `benchmark.py` with `run_buy_and_hold_backtest` and `compare_to_benchmark`.
2. Use the same fill timing and cost model as the MA simulator so comparisons are apples-to-apples.
3. Emit a `benchmark` block in the research report with passive metrics, `alpha` (strategy minus benchmark return), and `relative_drawdown` (strategy minus benchmark drawdown).
4. Default benchmark name is `buy_and_hold`; the interface accepts a name for future alternates.

## Consequences

- Alpha is total-return difference, not CAPM-style regression alpha.
- Buy-and-hold incurs a single entry cost when costs are enabled.
- Walk-forward summaries remain strategy-only; benchmark comparison applies to the full-sample backtest in the report.
