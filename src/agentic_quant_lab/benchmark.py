"""Buy-and-hold benchmark and strategy-relative comparison."""

from dataclasses import dataclass

import pandas as pd

from agentic_quant_lab.backtest import BacktestResult
from agentic_quant_lab.costs import CostAssumptions, compute_trade_costs


@dataclass(frozen=True)
class BenchmarkComparison:
    name: str
    benchmark_total_return: float
    benchmark_max_drawdown: float
    benchmark_volatility: float
    alpha: float
    relative_drawdown: float

    def to_artifact(self) -> dict:
        return {
            "name": self.name,
            "total_return": round(self.benchmark_total_return, 4),
            "max_drawdown": round(self.benchmark_max_drawdown, 4),
            "volatility": round(self.benchmark_volatility, 4),
            "alpha": round(self.alpha, 4),
            "relative_drawdown": round(self.relative_drawdown, 4),
        }


def run_buy_and_hold_backtest(
    prices: pd.DataFrame,
    cash: float,
    costs: CostAssumptions | None = None,
) -> BacktestResult:
    """Fully invested benchmark using the same fill timing as the MA simulator."""
    if "close" not in prices:
        raise ValueError("prices must contain a close column")

    assumptions = costs or CostAssumptions()
    frame = prices.copy()
    frame["signal"] = 1
    frame["position"] = frame["signal"].shift(1).fillna(0)
    frame["asset_return"] = frame["close"].pct_change().fillna(0)
    frame["position_change"] = frame["position"].diff().abs().fillna(0)
    spread = frame["spread_bps"] if "spread_bps" in frame.columns else None
    frame["trade_cost"] = compute_trade_costs(frame["position_change"], assumptions, spread)
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


def compare_to_benchmark(
    strategy: BacktestResult,
    benchmark: BacktestResult,
    *,
    name: str = "buy_and_hold",
) -> BenchmarkComparison:
    """Express strategy performance relative to a passive benchmark."""
    return BenchmarkComparison(
        name=name,
        benchmark_total_return=benchmark.total_return,
        benchmark_max_drawdown=benchmark.max_drawdown,
        benchmark_volatility=benchmark.volatility,
        alpha=strategy.total_return - benchmark.total_return,
        relative_drawdown=strategy.max_drawdown - benchmark.max_drawdown,
    )
