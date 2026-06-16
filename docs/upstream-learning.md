# Upstream Learning Notes

This repository studies patterns from widely used quant and agent-orchestration systems. Forks live under [@mastroke](https://github.com/mastroke):

| Upstream | Fork | What we studied |
| --- | --- | --- |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | [mastroke/vectorbt](https://github.com/mastroke/vectorbt) | Vectorized metrics, fold-style evaluation discipline |
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | [mastroke/backtesting.py](https://github.com/mastroke/backtesting.py) | Explicit commission/spread modeling on trades |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | [mastroke/langgraph](https://github.com/mastroke/langgraph) | StateGraph nodes for planner → simulator → risk flow |

## backtesting.py patterns adopted

| Pattern | Upstream reference | Implemented here |
| --- | --- | --- |
| Commission on position changes | `Backtest(..., commission=...)` | `CostAssumptions` in `costs.py` |
| Trade-cost drag in returns | `backtesting/backtesting.py` broker logic | `trade_cost` column in `backtest.py` |

## vectorbt patterns adopted

| Pattern | Upstream reference | Implemented here |
| --- | --- | --- |
| Contiguous fold evaluation | portfolio split / rolling analysis docs | `run_walk_forward_backtest()` in `walk_forward.py` |
| Aggregate fold metrics | multi-period reporting | `WalkForwardResult.to_summary()` |

## LangGraph patterns adopted

| Pattern | Upstream reference | Implemented here |
| --- | --- | --- |
| Explicit stage graph (planner → sim → risk) | `StateGraph.add_node` | Documented in README mermaid; `ResearchPlan.to_artifact()` as handoff contract |

## What is intentionally not ported yet

- vectorbt full vectorized portfolio engine
- backtesting.py Strategy class hierarchy and broker margin models
- LangGraph runtime — planner remains deterministic Python for testability

## Suggested reading order

1. backtesting.py `Backtest` commission parameters — cost modeling
2. vectorbt portfolio metrics docs — fold reporting mindset
3. LangGraph `StateGraph` tutorial — orchestration boundaries

## Next implementation targets

- Regime labels on fold summaries
- FinRL-style train/test embargo windows
- LangGraph adapter behind `build_research_plan` for LLM-generated hypotheses
