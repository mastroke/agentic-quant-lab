# ADR 0004: Risk-adjusted return metrics

## Status

Accepted

## Context

Backtests report total return, drawdown and volatility, but research reviews often need comparable risk-adjusted ratios. These must use explicit formulas and stay consistent with the simulator's 252-day annualization.

## Decision

1. Add `metrics.py` with `sharpe_ratio`, `sortino_ratio`, `calmar_ratio`, and `compute_risk_adjusted_metrics`.
2. Annualize with `sqrt(periods_per_year)` on periodic returns; default `periods_per_year=252`.
3. Sharpe uses sample standard deviation of excess returns (`ddof=1`).
4. Sortino uses root-mean-square of returns below the minimum acceptable return (MAR); MAR defaults to the per-period risk-free rate.
5. Calmar divides CAGR (compounded end equity, annualized) by the absolute peak-to-trough drawdown.
6. Lock expected values in `tests/fixtures/metrics_returns.json` for regression checks.

## Consequences

- Metrics are pure functions over return series; the MA backtest does not emit them until wired in.
- Undefined ratios (zero volatility or no downside) return `0.0` when mean excess is zero, otherwise `inf`.
- Future report and walk-forward summaries can import the same module without duplicating formulas.
