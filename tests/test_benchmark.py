import pytest

from agentic_quant_lab.backtest import BacktestResult, run_moving_average_backtest
from agentic_quant_lab.benchmark import compare_to_benchmark, run_buy_and_hold_backtest
from agentic_quant_lab.cli import build_report
from agentic_quant_lab.costs import CostAssumptions
from agentic_quant_lab.data import load_demo_prices


def test_buy_and_hold_tracks_asset_returns() -> None:
    prices = load_demo_prices()
    result = run_buy_and_hold_backtest(prices, cash=10_000, costs=CostAssumptions(0, 0))
    asset_return = float(prices["close"].iloc[-1] / prices["close"].iloc[0] - 1)

    assert result.trades == 1
    assert abs(result.total_return - asset_return) < 0.01


def test_benchmark_alpha_is_strategy_minus_passive() -> None:
    prices = load_demo_prices()
    costs = CostAssumptions(0, 0)
    strategy = run_moving_average_backtest(prices, cash=10_000, costs=costs)
    passive = run_buy_and_hold_backtest(prices, cash=10_000, costs=costs)
    comparison = compare_to_benchmark(strategy, passive)

    assert comparison.name == "buy_and_hold"
    assert comparison.alpha == strategy.total_return - passive.total_return
    assert comparison.benchmark_total_return == passive.total_return
    assert comparison.relative_drawdown == strategy.max_drawdown - passive.max_drawdown


def test_report_includes_benchmark_section() -> None:
    report = build_report(symbol="demo", cash=10_000)
    benchmark = report["benchmark"]

    assert benchmark["name"] == "buy_and_hold"
    assert "alpha" in benchmark
    assert "total_return" in benchmark
    assert "relative_drawdown" in benchmark


def test_compare_to_benchmark_computes_alpha_and_relative_drawdown() -> None:
    passive = BacktestResult(
        total_return=0.05,
        max_drawdown=-0.10,
        volatility=0.12,
        trades=1,
        equity_curve=[10_500.0],
    )
    strategy = BacktestResult(
        total_return=0.08,
        max_drawdown=-0.08,
        volatility=0.15,
        trades=4,
        equity_curve=[10_800.0],
    )

    comparison = compare_to_benchmark(strategy, passive)

    assert comparison.alpha == pytest.approx(0.03)
    assert comparison.relative_drawdown == pytest.approx(0.02)
