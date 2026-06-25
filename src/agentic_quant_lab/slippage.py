"""Pluggable slippage models applied on position changes."""

from dataclasses import dataclass
from typing import Protocol


class SlippageModel(Protocol):
    """Return slippage drag per unit of position change as a return fraction."""

    def rate(self, position_change: float, *, spread_bps: float | None = None) -> float:
        ...


@dataclass(frozen=True)
class FixedSlippage:
    """Constant basis-point slippage independent of trade size."""

    slippage_bps: float = 5.0

    def rate(self, position_change: float, *, spread_bps: float | None = None) -> float:
        return self.slippage_bps / 10_000


@dataclass(frozen=True)
class ProportionalSlippage:
    """Slippage that scales with the magnitude of the position change."""

    coefficient_bps: float = 5.0

    def rate(self, position_change: float, *, spread_bps: float | None = None) -> float:
        return (self.coefficient_bps / 10_000) * abs(position_change)


@dataclass(frozen=True)
class SpreadBasedSlippage:
    """Slippage derived from quoted bid-ask spread in basis points."""

    spread_bps: float = 10.0
    pay_half_spread: bool = True

    def rate(self, position_change: float, *, spread_bps: float | None = None) -> float:
        effective_spread = spread_bps if spread_bps is not None else self.spread_bps
        multiplier = 0.5 if self.pay_half_spread else 1.0
        return (effective_spread * multiplier) / 10_000
