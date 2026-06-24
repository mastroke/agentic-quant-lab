from dataclasses import dataclass


@dataclass(frozen=True)
class VolatilityTarget:
    """Scale exposure inversely with realized volatility toward a target level."""

    target_volatility: float = 0.15
    min_exposure: float = 0.0
    max_exposure: float = 1.0
    vol_floor: float = 1e-8

    def __post_init__(self) -> None:
        if self.target_volatility <= 0:
            raise ValueError("target_volatility must be positive")
        if self.min_exposure < 0:
            raise ValueError("min_exposure must be non-negative")
        if self.max_exposure < self.min_exposure:
            raise ValueError("max_exposure must be >= min_exposure")
        if self.vol_floor <= 0:
            raise ValueError("vol_floor must be positive")


def volatility_target_exposure(
    realized_volatility: float,
    config: VolatilityTarget | None = None,
) -> float:
    """Return bounded exposure weight: target_vol / realized_vol."""
    if realized_volatility < 0:
        raise ValueError("realized_volatility must be non-negative")

    settings = config or VolatilityTarget()
    effective_vol = max(realized_volatility, settings.vol_floor)
    raw_exposure = settings.target_volatility / effective_vol
    return max(settings.min_exposure, min(settings.max_exposure, raw_exposure))
