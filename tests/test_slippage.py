import pandas as pd
import pytest

from agentic_quant_lab.backtest import run_moving_average_backtest
from agentic_quant_lab.costs import CostAssumptions, compute_trade_costs, resolve_slippage
from agentic_quant_lab.data import load_demo_prices
from agentic_quant_lab.slippage import (
    FixedSlippage,
    ProportionalSlippage,
    SpreadBasedSlippage,
)


def test_fixed_slippage_rate_is_constant() -> None:
    model = FixedSlippage(slippage_bps=8.0)

    assert model.rate(0.0) == pytest.approx(8.0 / 10_000)
    assert model.rate(1.0) == pytest.approx(8.0 / 10_000)
    assert model.rate(0.5) == pytest.approx(8.0 / 10_000)


def test_proportional_slippage_scales_with_trade_size() -> None:
    model = ProportionalSlippage(coefficient_bps=10.0)

    assert model.rate(0.5) == pytest.approx(0.5 * 10.0 / 10_000)
    assert model.rate(1.0) == pytest.approx(10.0 / 10_000)
    assert model.rate(-1.0) == pytest.approx(10.0 / 10_000)


def test_spread_based_slippage_uses_half_spread_by_default() -> None:
    model = SpreadBasedSlippage(spread_bps=20.0)

    assert model.rate(1.0) == pytest.approx(10.0 / 10_000)


def test_spread_based_slippage_accepts_per_bar_override() -> None:
    model = SpreadBasedSlippage(spread_bps=20.0, pay_half_spread=False)

    assert model.rate(1.0, spread_bps=40.0) == pytest.approx(40.0 / 10_000)


def test_resolve_slippage_falls_back_to_legacy_bps() -> None:
    resolved = resolve_slippage(7.5, None)

    assert isinstance(resolved, FixedSlippage)
    assert resolved.slippage_bps == 7.5


def test_trade_cost_matches_legacy_fixed_rate() -> None:
    assumptions = CostAssumptions(commission_bps=10.0, slippage_bps=5.0)

    assert assumptions.trade_cost(1.0) == pytest.approx(assumptions.per_trade_rate)


def test_proportional_slippage_increases_cost_drag() -> None:
    prices = load_demo_prices()
    fixed = run_moving_average_backtest(
        prices,
        cash=10_000,
        costs=CostAssumptions(
            commission_bps=0.0,
            slippage_model=FixedSlippage(slippage_bps=10.0),
        ),
    )
    proportional = run_moving_average_backtest(
        prices,
        cash=10_000,
        costs=CostAssumptions(
            commission_bps=0.0,
            slippage_model=ProportionalSlippage(coefficient_bps=10.0),
        ),
    )

    assert proportional.cost_drag >= fixed.cost_drag


def test_spread_column_feeds_spread_based_model() -> None:
    prices = load_demo_prices().head(80).copy()
    prices["spread_bps"] = 30.0
    assumptions = CostAssumptions(
        commission_bps=0.0,
        slippage_model=SpreadBasedSlippage(spread_bps=5.0),
    )
    position_changes = pd.Series([0.0, 1.0, 0.0, 1.0])

    costs = compute_trade_costs(position_changes, assumptions, prices["spread_bps"].head(4))

    assert costs.iloc[1] == pytest.approx(15.0 / 10_000)
    assert costs.iloc[3] == pytest.approx(15.0 / 10_000)
