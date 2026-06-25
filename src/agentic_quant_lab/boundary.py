"""Research vs execution boundary enforcement."""

from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):
    """Bounded outcomes the research pipeline may emit."""

    RESEARCH_ONLY = "research_only"
    PAPER_TRADE_ONLY = "paper_trade_only"


ALLOWED_DECISIONS: frozenset[str] = frozenset(mode.value for mode in ExecutionMode)

_FORBIDDEN_DECISIONS: frozenset[str] = frozenset(
    {
        "live",
        "live_trade",
        "live_trading",
        "execute",
        "execute_order",
        "submit_order",
    }
)


def validate_decision(decision: str) -> ExecutionMode:
    """Reject unknown or live-trading decision strings before they reach reports."""
    normalized = decision.strip().lower()
    if normalized in _FORBIDDEN_DECISIONS:
        raise ValueError(
            f"Live execution decision {decision!r} is out of scope. "
            f"Allowed modes: {sorted(ALLOWED_DECISIONS)}."
        )
    try:
        return ExecutionMode(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Unknown execution decision {decision!r}. "
            f"Allowed modes: {sorted(ALLOWED_DECISIONS)}."
        ) from exc
