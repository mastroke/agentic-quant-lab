from dataclasses import dataclass

import pandas as pd

from agentic_quant_lab.costs import CostAssumptions


@dataclass(frozen=True)
class BacktestResult:
    total_return: float
    max_drawdown: float
    volatility: float
    trades: int
    equity_curve: list[float]
    cost_drag: float = 0.0


def run_moving_average_backtest(
    prices: pd.DataFrame,
    cash: float,
    short_window: int = 10,
    long_window: int = 40,
    costs: CostAssumptions | None = None,
) -> BacktestResult:
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")
    if "close" not in prices:
        raise ValueError("prices must contain a close column")

    assumptions = costs or CostAssumptions()
    frame = prices.copy()
    frame["short_ma"] = frame["close"].rolling(short_window).mean()
    frame["long_ma"] = frame["close"].rolling(long_window).mean()
    frame["signal"] = (frame["short_ma"] > frame["long_ma"]).astype(int)
    frame["position"] = frame["signal"].shift(1).fillna(0)
    frame["asset_return"] = frame["close"].pct_change().fillna(0)
    frame["position_change"] = frame["position"].diff().abs().fillna(0)
    frame["trade_cost"] = frame["position_change"] * assumptions.per_trade_rate
    frame["strategy_return"] = frame["position"] * frame["asset_return"] - frame["trade_cost"]
    frame["equity"] = cash * (1 + frame["strategy_return"]).cumprod()

    peak = frame["equity"].cummax()
    drawdown = frame["equity"] / peak - 1
    trades = int(frame["position_change"].sum())

    return BacktestResult(
        total_return=float(frame["equity"].iloc[-1] / cash - 1),
        max_drawdown=float(drawdown.min()),
        volatility=float(frame["strategy_return"].std() * (252**0.5)),
        trades=trades,
        equity_curve=[round(float(value), 2) for value in frame["equity"].tail(20)],
        cost_drag=float(frame["trade_cost"].sum()),
    )

