"""Agentic quantitative research lab."""

from agentic_quant_lab.backtest import BacktestResult, run_moving_average_backtest
from agentic_quant_lab.metrics import (
    RiskAdjustedMetrics,
    calmar_ratio,
    compute_risk_adjusted_metrics,
    max_drawdown_from_returns,
    sharpe_ratio,
    sortino_ratio,
)
from agentic_quant_lab.risk import RiskDecision, evaluate_risk
from agentic_quant_lab.sizing import VolatilityTarget, volatility_target_exposure
from agentic_quant_lab.sweep import sweep_moving_average_windows

__all__ = [
    "BacktestResult",
    "RiskAdjustedMetrics",
    "RiskDecision",
    "VolatilityTarget",
    "calmar_ratio",
    "compute_risk_adjusted_metrics",
    "evaluate_risk",
    "max_drawdown_from_returns",
    "run_moving_average_backtest",
    "sharpe_ratio",
    "sortino_ratio",
    "sweep_moving_average_windows",
    "volatility_target_exposure",
]

