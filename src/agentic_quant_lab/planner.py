from dataclasses import dataclass, asdict

from agentic_quant_lab.costs import CostAssumptions


@dataclass(frozen=True)
class WalkForwardConfig:
    n_folds: int = 3


@dataclass(frozen=True)
class ResearchPlan:
    symbol: str
    hypothesis: str
    strategy: str
    guardrails: list[str]
    cost_assumptions: CostAssumptions = CostAssumptions()
    walk_forward: WalkForwardConfig = WalkForwardConfig()

    def to_artifact(self) -> dict:
        """Structured experiment plan for agents, simulators and audit trails."""
        return {
            "symbol": self.symbol,
            "hypothesis": self.hypothesis,
            "strategy": self.strategy,
            "guardrails": list(self.guardrails),
            "cost_assumptions": asdict(self.cost_assumptions),
            "walk_forward": asdict(self.walk_forward),
        }


def build_research_plan(symbol: str) -> ResearchPlan:
    """Create a deterministic plan that an agent can hand to the simulator."""
    return ResearchPlan(
        symbol=symbol.upper(),
        hypothesis="Trend persistence can be tested with a short/long moving-average crossover.",
        strategy="moving_average_crossover",
        guardrails=[
            "Reject if max drawdown is worse than -12%.",
            "Reject if annualized volatility is above 35%.",
            "Treat all positive results as paper-trading candidates only.",
        ],
        cost_assumptions=CostAssumptions(commission_bps=10.0, slippage_bps=5.0),
        walk_forward=WalkForwardConfig(n_folds=3),
    )

