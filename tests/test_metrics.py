import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agentic_quant_lab.metrics import (
    RiskAdjustedMetrics,
    calmar_ratio,
    compute_risk_adjusted_metrics,
    max_drawdown_from_returns,
    sharpe_ratio,
    sortino_ratio,
)

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "metrics_returns.json"


def _load_metric_fixtures() -> dict:
    with FIXTURES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.parametrize("fixture_name", ["mixed_returns", "drawdown_window"])
def test_metrics_match_known_fixtures(fixture_name: str) -> None:
    fixture = _load_metric_fixtures()[fixture_name]
    returns = fixture["returns"]

    assert max_drawdown_from_returns(returns) == pytest.approx(fixture["max_drawdown"])
    assert sharpe_ratio(returns) == pytest.approx(fixture["sharpe"])
    assert sortino_ratio(returns) == pytest.approx(fixture["sortino"])
    assert calmar_ratio(returns) == pytest.approx(fixture["calmar"])

    bundle = compute_risk_adjusted_metrics(returns)
    assert isinstance(bundle, RiskAdjustedMetrics)
    assert bundle.sharpe == pytest.approx(fixture["sharpe"])
    assert bundle.sortino == pytest.approx(fixture["sortino"])
    assert bundle.calmar == pytest.approx(fixture["calmar"])


def test_sharpe_uses_risk_free_rate() -> None:
    returns = [0.02, 0.01, 0.015, 0.005]
    without_rf = sharpe_ratio(returns, risk_free_rate=0.0)
    with_rf = sharpe_ratio(returns, risk_free_rate=0.10)

    assert with_rf < without_rf


def test_calmar_accepts_precomputed_drawdown() -> None:
    returns = [0.01, -0.005, 0.008, -0.002, 0.006]
    explicit = calmar_ratio(returns, max_drawdown=-0.01)
    assert explicit != calmar_ratio(returns)


def test_metrics_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="empty"):
        sharpe_ratio([])

    with pytest.raises(ValueError, match="at least two"):
        sharpe_ratio([0.01])

    with pytest.raises(ValueError, match="periods_per_year"):
        sortino_ratio([0.01, -0.01], periods_per_year=0)

    with pytest.raises(ValueError, match="max_drawdown must be negative"):
        calmar_ratio([0.01, 0.02], max_drawdown=0.0)


def test_sharpe_handles_zero_excess_volatility() -> None:
    returns = [0.001, 0.001, 0.001, 0.001]
    assert sharpe_ratio(returns) == pytest.approx(float("inf"))


def test_sortino_handles_no_downside() -> None:
    returns = [0.01, 0.02, 0.015, 0.008]
    assert sortino_ratio(returns) == pytest.approx(float("inf"))


def test_metrics_accept_numpy_and_pandas_inputs() -> None:
    fixture = _load_metric_fixtures()["mixed_returns"]
    array = np.asarray(fixture["returns"])
    series = pd.Series(fixture["returns"])

    assert sharpe_ratio(array) == pytest.approx(fixture["sharpe"])
    assert sortino_ratio(series) == pytest.approx(fixture["sortino"])
