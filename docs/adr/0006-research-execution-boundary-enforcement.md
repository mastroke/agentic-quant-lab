# ADR 0006: Research vs execution boundary enforcement

## Status

Accepted

## Context

[ADR 0001](0001-research-only-boundary.md) sets scope: this repository produces research reports and paper-trading candidates only. Scope alone does not prevent accidental live-trading paths as the codebase grows — new modules, agent adapters, or report fields could introduce broker hooks or unbounded decision strings unless enforcement is explicit and tested.

Quant systems should separate **research**, **paper trading**, and **live execution** at architectural seams, not only in README disclaimers.

## Decision

Enforce the research-only boundary at multiple layers:

| Layer | Mechanism | Location |
| --- | --- | --- |
| Scope | Live execution out of scope; paper trading is the maximum outcome | ADR 0001, README |
| Dependencies | No broker or exchange SDKs in `pyproject.toml` | `pyproject.toml` |
| Data ingress | Synthetic demo prices only; no authenticated market-data or order APIs | `data.py` |
| Pipeline shape | Planner → simulator → risk → JSON report; no order-submission stage | `cli.py`, README mermaid |
| Typed outcomes | `ExecutionMode` enum limits decisions to `research_only` and `paper_trade_only` | `boundary.py` |
| Risk gate | `evaluate_risk` emits only bounded modes; `RiskDecision` validates on construction | `risk.py` |
| Export gate | `build_report` re-validates the decision before JSON serialization | `cli.py` |
| Planner contract | Guardrails state that positive results are paper-trading candidates only | `planner.py` |
| Tests | Reject live decision strings; AST scan blocks broker SDK imports in package source | `tests/test_boundary.py` |

`validate_decision()` rejects known live-execution strings (for example `live_trade`, `submit_order`) and unknown values before they reach reports or downstream tooling.

Live execution, if added later, must live in a **separate repository or service** with its own permission model, audit trail, and deployment boundary — not as an extension of this research pipeline.

## Consequences

- Accidental live-trading paths fail fast at decision construction or report export instead of silently propagating.
- The public package exports `ExecutionMode`, `ALLOWED_DECISIONS`, and `validate_decision` so adapters and eval harnesses can reuse the same contract.
- Adding a broker SDK or a third decision value requires an explicit ADR and test updates; CI will fail on forbidden imports.
- Paper-trading remains a **label** in research output, not an integrated paper-trading engine — this ADR does not add one.
