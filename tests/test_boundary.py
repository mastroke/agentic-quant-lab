import ast
from pathlib import Path

import pytest

from agentic_quant_lab.boundary import ALLOWED_DECISIONS, ExecutionMode, validate_decision
from agentic_quant_lab.risk import RiskDecision


def test_validate_decision_accepts_bounded_modes() -> None:
    assert validate_decision("research_only") is ExecutionMode.RESEARCH_ONLY
    assert validate_decision("paper_trade_only") is ExecutionMode.PAPER_TRADE_ONLY


@pytest.mark.parametrize(
    "decision",
    [
        "live",
        "live_trade",
        "live_trading",
        "execute_order",
        "submit_order",
        "production_trade",
    ],
)
def test_validate_decision_rejects_live_execution_paths(decision: str) -> None:
    with pytest.raises(ValueError, match="out of scope|Unknown execution"):
        validate_decision(decision)


def test_risk_decision_rejects_unbounded_outcome_at_construction() -> None:
    with pytest.raises(ValueError, match="Unknown execution decision"):
        RiskDecision(decision="broker_execute", notes=["should not pass"])


def test_allowed_decisions_match_execution_mode_values() -> None:
    assert ALLOWED_DECISIONS == {mode.value for mode in ExecutionMode}


def test_package_source_has_no_broker_execution_imports() -> None:
    package_root = Path(__file__).resolve().parents[1] / "src" / "agentic_quant_lab"
    forbidden_modules = frozenset({"alpaca", "ib_insync", "ccxt", "robin_stocks"})

    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", maxsplit=1)[0]
                    assert root not in forbidden_modules, f"{root!r} imported in {path.name}"
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                root = node.module.split(".", maxsplit=1)[0]
                assert root not in forbidden_modules, f"{root!r} imported in {path.name}"
