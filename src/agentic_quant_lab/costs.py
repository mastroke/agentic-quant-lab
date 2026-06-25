from dataclasses import dataclass

import pandas as pd

from agentic_quant_lab.slippage import FixedSlippage, SlippageModel


def resolve_slippage(
    slippage_bps: float,
    slippage_model: SlippageModel | None,
) -> SlippageModel:
    if slippage_model is not None:
        return slippage_model
    return FixedSlippage(slippage_bps=slippage_bps)


@dataclass(frozen=True)
class CostAssumptions:
    """Per-side transaction costs inspired by backtesting.py commission modeling."""

    commission_bps: float = 10.0
    slippage_bps: float = 5.0
    slippage_model: SlippageModel | None = None

    @property
    def per_trade_rate(self) -> float:
        """Commission plus slippage rate for a unit position change (fixed slippage)."""
        model = resolve_slippage(self.slippage_bps, self.slippage_model)
        return self.commission_bps / 10_000 + model.rate(1.0)

    def trade_cost(
        self,
        position_change: float,
        *,
        spread_bps: float | None = None,
    ) -> float:
        if position_change == 0:
            return 0.0
        model = resolve_slippage(self.slippage_bps, self.slippage_model)
        magnitude = abs(position_change)
        commission = magnitude * self.commission_bps / 10_000
        slippage = magnitude * model.rate(position_change, spread_bps=spread_bps)
        return commission + slippage


def compute_trade_costs(
    position_changes: pd.Series,
    assumptions: CostAssumptions,
    spread_bps: pd.Series | None = None,
) -> pd.Series:
    """Vectorized trade costs for a series of absolute position changes."""
    costs: list[float] = []
    for index, position_change in enumerate(position_changes):
        bar_spread = None
        if spread_bps is not None:
            bar_spread = float(spread_bps.iloc[index])
        costs.append(assumptions.trade_cost(float(position_change), spread_bps=bar_spread))
    return pd.Series(costs, index=position_changes.index)
