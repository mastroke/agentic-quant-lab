import pandas as pd
import pytest

from agentic_quant_lab.data import load_demo_prices
from agentic_quant_lab.sweep import sweep_moving_average_windows


def test_sweep_returns_ranked_frame_with_expected_columns() -> None:
    frame = sweep_moving_average_windows(
        load_demo_prices(),
        cash=10_000,
        short_windows=(5, 10),
        long_windows=(30, 40),
    )

    assert list(frame.columns) == [
        "rank",
        "short_window",
        "long_window",
        "total_return",
        "max_drawdown",
        "volatility",
        "trades",
        "cost_drag",
    ]
    assert len(frame) == 4
    assert frame["rank"].tolist() == [1, 2, 3, 4]
    assert frame["total_return"].is_monotonic_decreasing


def test_sweep_is_reproducible_across_runs() -> None:
    prices = load_demo_prices(rows=200, seed=11)
    kwargs = {
        "cash": 10_000.0,
        "short_windows": (8, 12, 16),
        "long_windows": (24, 36, 48),
    }

    first = sweep_moving_average_windows(prices, **kwargs)
    second = sweep_moving_average_windows(prices, **kwargs)

    pd.testing.assert_frame_equal(first, second)


def test_sweep_tie_breaks_on_window_pairs() -> None:
    prices = load_demo_prices(rows=120, seed=3)
    frame = sweep_moving_average_windows(
        prices,
        cash=10_000,
        short_windows=(5, 10),
        long_windows=(20, 40),
    )

    tied = frame[frame["total_return"] == frame["total_return"].iloc[0]]
    if len(tied) > 1:
        pairs = list(zip(tied["short_window"], tied["long_window"], strict=True))
        assert pairs == sorted(pairs)


def test_sweep_skips_invalid_window_pairs() -> None:
    frame = sweep_moving_average_windows(
        load_demo_prices(),
        cash=10_000,
        short_windows=(40, 10),
        long_windows=(20, 30),
    )

    assert set(frame["short_window"]).issubset({10})
    assert all(frame["short_window"] < frame["long_window"])


def test_sweep_rejects_empty_or_invalid_grids() -> None:
    prices = load_demo_prices()

    with pytest.raises(ValueError, match="non-empty"):
        sweep_moving_average_windows(prices, cash=10_000, short_windows=())

    with pytest.raises(ValueError, match="at least 1"):
        sweep_moving_average_windows(prices, cash=10_000, short_windows=(0, 5))

    with pytest.raises(ValueError, match="no valid"):
        sweep_moving_average_windows(
            prices,
            cash=10_000,
            short_windows=(50,),
            long_windows=(10, 20),
        )
