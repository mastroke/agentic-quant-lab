# ADR 0003: Volatility-target position sizing

## Status

Accepted

## Context

The baseline simulator uses binary long/flat positions. Research workflows often scale exposure so portfolio volatility tracks a target rather than toggling full notional on every signal.

## Decision

1. Add `VolatilityTarget` config and `volatility_target_exposure()` in `sizing.py`.
2. Compute weight as `target_vol / realized_vol`, clipped to `[min_exposure, max_exposure]`.
3. Apply a `vol_floor` when realized volatility is near zero to avoid unbounded leverage.

## Consequences

- Sizing is a standalone module; the MA backtest still defaults to 0/1 positions until wired in.
- Bounds and invalid inputs fail fast with explicit errors for testability.
- Future simulators can multiply signal strength by the sizing weight before cost application.
