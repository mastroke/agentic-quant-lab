"""Risk-adjusted return metrics for strategy evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RiskAdjustedMetrics:
    sharpe: float
    sortino: float
    calmar: float


def _to_returns_array(returns: pd.Series | np.ndarray | list[float]) -> np.ndarray:
    array = np.asarray(returns, dtype=float)
    if array.ndim != 1:
        raise ValueError("returns must be one-dimensional")
    if array.size == 0:
        raise ValueError("returns must not be empty")
    return array


def max_drawdown_from_returns(returns: pd.Series | np.ndarray | list[float]) -> float:
    """Peak-to-trough drawdown on a cumulative return curve (negative when underwater)."""
    series = _to_returns_array(returns)
    equity = np.cumprod(1.0 + series)
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    return float(drawdown.min())


def sharpe_ratio(
    returns: pd.Series | np.ndarray | list[float],
    *,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Annualized Sharpe: mean(excess) / std(excess) * sqrt(periods_per_year).

    excess_t = r_t - risk_free_rate / periods_per_year
    """
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")

    series = _to_returns_array(returns)
    if series.size < 2:
        raise ValueError("sharpe_ratio requires at least two return observations")

    rf_per_period = risk_free_rate / periods_per_year
    excess = series - rf_per_period
    volatility = excess.std(ddof=1)
    if volatility == 0.0:
        return 0.0 if excess.mean() == 0.0 else float("inf")

    return float(excess.mean() / volatility * np.sqrt(periods_per_year))


def sortino_ratio(
    returns: pd.Series | np.ndarray | list[float],
    *,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    mar: float | None = None,
) -> float:
    """Annualized Sortino: mean(excess) / downside_deviation * sqrt(periods_per_year).

    downside_deviation = sqrt(mean(min(r_t - target, 0)^2))
    target defaults to the per-period risk-free rate when mar is omitted.
    """
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")

    series = _to_returns_array(returns)
    if series.size < 2:
        raise ValueError("sortino_ratio requires at least two return observations")

    target = mar if mar is not None else risk_free_rate / periods_per_year
    excess = series - target
    downside = np.minimum(excess, 0.0)
    downside_deviation = float(np.sqrt(np.mean(downside**2)))
    if downside_deviation == 0.0:
        return 0.0 if excess.mean() == 0.0 else float("inf")

    return float(excess.mean() / downside_deviation * np.sqrt(periods_per_year))


def calmar_ratio(
    returns: pd.Series | np.ndarray | list[float],
    *,
    periods_per_year: int = 252,
    max_drawdown: float | None = None,
) -> float:
    """Calmar ratio: CAGR / |max_drawdown|.

    CAGR = (equity_end)^(periods_per_year / n) - 1
    max_drawdown is the peak-to-trough loss (negative); magnitude is used.
    """
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")

    series = _to_returns_array(returns)
    drawdown = max_drawdown if max_drawdown is not None else max_drawdown_from_returns(series)
    if drawdown >= 0.0:
        raise ValueError("max_drawdown must be negative when underwater")

    equity_end = float(np.prod(1.0 + series))
    cagr = equity_end ** (periods_per_year / series.size) - 1.0
    return float(cagr / abs(drawdown))


def compute_risk_adjusted_metrics(
    returns: pd.Series | np.ndarray | list[float],
    *,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    mar: float | None = None,
    max_drawdown: float | None = None,
) -> RiskAdjustedMetrics:
    """Compute Sharpe, Sortino and Calmar for a return series."""
    return RiskAdjustedMetrics(
        sharpe=sharpe_ratio(
            returns,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        ),
        sortino=sortino_ratio(
            returns,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
            mar=mar,
        ),
        calmar=calmar_ratio(
            returns,
            periods_per_year=periods_per_year,
            max_drawdown=max_drawdown,
        ),
    )
