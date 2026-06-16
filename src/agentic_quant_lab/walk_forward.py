from dataclasses import dataclass

import pandas as pd

from agentic_quant_lab.backtest import BacktestResult, run_moving_average_backtest
from agentic_quant_lab.costs import CostAssumptions


@dataclass(frozen=True)
class FoldResult:
    fold: int
    rows: int
    result: BacktestResult


@dataclass(frozen=True)
class WalkForwardResult:
    folds: tuple[FoldResult, ...]
    mean_return: float
    worst_drawdown: float
    total_trades: int

    def to_summary(self) -> dict:
        return {
            "n_folds": len(self.folds),
            "mean_return": round(self.mean_return, 4),
            "worst_drawdown": round(self.worst_drawdown, 4),
            "total_trades": self.total_trades,
            "fold_returns": [round(f.result.total_return, 4) for f in self.folds],
        }


def run_walk_forward_backtest(
    prices: pd.DataFrame,
    cash: float,
    n_folds: int = 3,
    short_window: int = 10,
    long_window: int = 40,
    costs: CostAssumptions | None = None,
) -> WalkForwardResult:
    """Evaluate strategy on contiguous out-of-sample folds (vectorbt-style split discipline)."""
    if n_folds < 1:
        raise ValueError("n_folds must be at least 1")
    if len(prices) < long_window + 5:
        raise ValueError("not enough rows for walk-forward evaluation")

    segments = _split_contiguous_folds(prices, n_folds)
    fold_results: list[FoldResult] = []

    for index, segment in enumerate(segments, start=1):
        if len(segment) < long_window + 2:
            continue
        result = run_moving_average_backtest(
            segment,
            cash=cash,
            short_window=short_window,
            long_window=long_window,
            costs=costs,
        )
        fold_results.append(FoldResult(fold=index, rows=len(segment), result=result))

    if not fold_results:
        raise ValueError("no fold produced a valid backtest")

    returns = [fold.result.total_return for fold in fold_results]
    drawdowns = [fold.result.max_drawdown for fold in fold_results]
    trades = sum(fold.result.trades for fold in fold_results)

    return WalkForwardResult(
        folds=tuple(fold_results),
        mean_return=float(sum(returns) / len(returns)),
        worst_drawdown=float(min(drawdowns)),
        total_trades=trades,
    )


def _split_contiguous_folds(frame: pd.DataFrame, n_folds: int) -> list[pd.DataFrame]:
    fold_size = len(frame) // n_folds
    if fold_size == 0:
        return [frame.copy()]
    segments: list[pd.DataFrame] = []
    for index in range(n_folds):
        start = index * fold_size
        end = start + fold_size if index < n_folds - 1 else len(frame)
        segments.append(frame.iloc[start:end].reset_index(drop=True))
    return segments
