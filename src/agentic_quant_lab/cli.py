import argparse
import json

from agentic_quant_lab.backtest import run_moving_average_backtest
from agentic_quant_lab.benchmark import compare_to_benchmark, run_buy_and_hold_backtest
from agentic_quant_lab.data import load_demo_prices
from agentic_quant_lab.planner import build_research_plan
from agentic_quant_lab.risk import evaluate_risk
from agentic_quant_lab.walk_forward import run_walk_forward_backtest


def build_report(symbol: str, cash: float) -> dict:
    plan = build_research_plan(symbol)
    prices = load_demo_prices()
    result = run_moving_average_backtest(
        prices=prices,
        cash=cash,
        costs=plan.cost_assumptions,
    )
    walk_forward = run_walk_forward_backtest(
        prices=prices,
        cash=cash,
        n_folds=plan.walk_forward.n_folds,
        costs=plan.cost_assumptions,
    )
    benchmark_result = run_buy_and_hold_backtest(
        prices=prices,
        cash=cash,
        costs=plan.cost_assumptions,
    )
    risk = evaluate_risk(result)

    return {
        "experiment_plan": plan.to_artifact(),
        "symbol": plan.symbol,
        "hypothesis": plan.hypothesis,
        "strategy": plan.strategy,
        "guardrails": plan.guardrails,
        "decision": risk.decision,
        "total_return": round(result.total_return, 4),
        "max_drawdown": round(result.max_drawdown, 4),
        "volatility": round(result.volatility, 4),
        "trades": result.trades,
        "cost_drag": round(result.cost_drag, 6),
        "benchmark": compare_to_benchmark(result, benchmark_result).to_artifact(),
        "walk_forward": walk_forward.to_summary(),
        "risk_notes": risk.notes,
        "equity_curve_tail": result.equity_curve,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="DEMO")
    parser.add_argument("--cash", type=float, default=10_000)
    args = parser.parse_args()
    print(json.dumps(build_report(symbol=args.symbol, cash=args.cash), indent=2))


if __name__ == "__main__":
    main()

