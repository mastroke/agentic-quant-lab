"""Deterministic grid sweep over moving-average crossover windows."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from agentic_quant_lab.backtest import run_moving_average_backtest
from agentic_quant_lab.costs import CostAssumptions

_DEFAULT_SHORT_WINDOWS: tuple[int, ...] = (5, 10, 15, 20)
_DEFAULT_LONG_WINDOWS: tuple[int, ...] = (30, 40, 50, 60)
_RESULT_COLUMNS: tuple[str, ...] = (
    "rank",
    "short_window",
    "long_window",
    "total_return",
    "max_drawdown",
    "volatility",
    "trades",
    "cost_drag",
)


def sweep_moving_average_windows(
    prices: pd.DataFrame,
    cash: float,
    short_windows: Sequence[int] | None = None,
    long_windows: Sequence[int] | None = None,
    costs: CostAssumptions | None = None,
) -> pd.DataFrame:
    """Run a deterministic grid over MA windows and return a ranked result frame.

  Iteration order is fixed (short grid, then long grid). Rows are ranked by
  ``total_return`` descending; ties break on ``short_window`` then ``long_window``.
  """
    shorts = tuple(short_windows if short_windows is not None else _DEFAULT_SHORT_WINDOWS)
    longs = tuple(long_windows if long_windows is not None else _DEFAULT_LONG_WINDOWS)

    if not shorts or not longs:
        raise ValueError("short_windows and long_windows must be non-empty")
    if any(window < 1 for window in (*shorts, *longs)):
        raise ValueError("window lengths must be at least 1")

    rows: list[dict[str, int | float]] = []
    for short_window in shorts:
        for long_window in longs:
            if short_window >= long_window:
                continue
            result = run_moving_average_backtest(
                prices,
                cash=cash,
                short_window=short_window,
                long_window=long_window,
                costs=costs,
            )
            rows.append(
                {
                    "short_window": short_window,
                    "long_window": long_window,
                    "total_return": result.total_return,
                    "max_drawdown": result.max_drawdown,
                    "volatility": result.volatility,
                    "trades": result.trades,
                    "cost_drag": result.cost_drag,
                }
            )

    if not rows:
        raise ValueError("no valid short/long window pairs in grid")

    frame = pd.DataFrame(rows)
    ranked = frame.sort_values(
        by=["total_return", "short_window", "long_window"],
        ascending=[False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    return ranked.loc[:, list(_RESULT_COLUMNS)]
