import pytest

from agentic_quant_lab.backtest import BacktestResult, run_moving_average_backtest
from agentic_quant_lab.cli import build_report
from agentic_quant_lab.costs import CostAssumptions
from agentic_quant_lab.data import load_demo_prices
from agentic_quant_lab.planner import build_research_plan
from agentic_quant_lab.risk import evaluate_risk
from agentic_quant_lab.sizing import VolatilityTarget, volatility_target_exposure
from agentic_quant_lab.walk_forward import run_walk_forward_backtest


def test_backtest_generates_metrics() -> None:
    result = run_moving_average_backtest(load_demo_prices(), cash=10_000)

    assert isinstance(result.total_return, float)
    assert result.max_drawdown <= 0
    assert result.volatility >= 0
    assert len(result.equity_curve) == 20


def test_transaction_costs_reduce_returns() -> None:
    prices = load_demo_prices()
    baseline = run_moving_average_backtest(prices, cash=10_000, costs=CostAssumptions(0, 0))
    with_costs = run_moving_average_backtest(
        prices,
        cash=10_000,
        costs=CostAssumptions(commission_bps=50, slippage_bps=50),
    )

    assert with_costs.cost_drag > 0
    assert with_costs.total_return <= baseline.total_return


def test_walk_forward_produces_fold_summary() -> None:
    summary = run_walk_forward_backtest(load_demo_prices(), cash=10_000, n_folds=3).to_summary()

    assert summary["n_folds"] == 3
    assert len(summary["fold_returns"]) == 3
    assert summary["total_trades"] >= 0


def test_research_plan_exports_artifact() -> None:
    artifact = build_research_plan("demo").to_artifact()

    assert artifact["symbol"] == "DEMO"
    assert "cost_assumptions" in artifact
    assert artifact["walk_forward"]["n_folds"] == 3


def test_risk_decision_is_bounded() -> None:
    result = run_moving_average_backtest(load_demo_prices(), cash=10_000)
    decision = evaluate_risk(result)

    assert decision.decision in {"paper_trade_only", "research_only"}
    assert decision.notes


def test_risk_rejects_when_drawdown_exceeds_limit() -> None:
    result = BacktestResult(
        total_return=0.05,
        max_drawdown=-0.20,
        volatility=0.10,
        trades=3,
        equity_curve=[10_000.0],
    )

    decision = evaluate_risk(result)

    assert decision.decision == "research_only"
    assert any("drawdown" in note.lower() for note in decision.notes)


def test_volatility_target_scales_inversely_with_realized_vol() -> None:
    config = VolatilityTarget(target_volatility=0.20, min_exposure=0.0, max_exposure=1.0)

    assert volatility_target_exposure(0.20, config) == 1.0
    assert volatility_target_exposure(0.40, config) == 0.5


def test_volatility_target_clips_to_bounds() -> None:
    config = VolatilityTarget(
        target_volatility=0.15,
        min_exposure=0.10,
        max_exposure=0.80,
        vol_floor=1e-8,
    )

    assert volatility_target_exposure(0.01, config) == 0.80
    assert volatility_target_exposure(5.0, config) == 0.10


def test_volatility_target_uses_floor_for_near_zero_vol() -> None:
    config = VolatilityTarget(target_volatility=0.15, max_exposure=1.0, vol_floor=0.05)

    assert volatility_target_exposure(0.0, config) == 1.0
    assert volatility_target_exposure(1e-12, config) == 1.0


def test_volatility_target_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="target_volatility"):
        VolatilityTarget(target_volatility=0.0)

    with pytest.raises(ValueError, match="max_exposure"):
        VolatilityTarget(min_exposure=0.5, max_exposure=0.2)

    with pytest.raises(ValueError, match="realized_volatility"):
        volatility_target_exposure(-0.01)


def test_report_is_reviewable() -> None:
    report = build_report(symbol="demo", cash=10_000)

    assert report["symbol"] == "DEMO"
    assert "experiment_plan" in report
    assert "walk_forward" in report
    assert "benchmark" in report
    assert report["benchmark"]["name"] == "buy_and_hold"
    assert "alpha" in report["benchmark"]
    assert "risk_notes" in report
    assert report["decision"] in {"paper_trade_only", "research_only"}
