from dataclasses import dataclass


@dataclass(frozen=True)
class CostAssumptions:
    """Per-side transaction costs inspired by backtesting.py commission modeling."""

    commission_bps: float = 10.0
    slippage_bps: float = 5.0

    @property
    def per_trade_rate(self) -> float:
        return (self.commission_bps + self.slippage_bps) / 10_000
