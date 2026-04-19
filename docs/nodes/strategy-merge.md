# Node 9d — `strategy_merge`

**File:** [`backend/app/graph/nodes/strategy_merge.py`](../../backend/app/graph/nodes/strategy_merge.py)

Fan-in after the three parallel execution agents.

## Purpose

Consolidate one top recommendation per framework into a ranked `merged_strategies` list consumed by `simulation`, `strategy_critic`, and `execution_architect`.

## Merge rule

For each agent, if the agent didn't error:

| Agent | Top recommendation pulled from | Extra fields |
|---|---|---|
| Unit Economist | `top_roi_intervention` or `proposed_interventions[0]` | `expected_roi`, `estimated_cost`, `cost_usd` |
| JTBD Specialist | `proposed_interventions[0]` | `expected_impact`, `job_focus`, `implementation_effort` |
| Growth Hacker | `proposed_tactics[0]` | `expected_lift`, `target_metric`, `implementation_timeline` |

All merged items share `rank`, `recommendation`, `framework`, `confidence`, `rationale`.

## Output

`strategy_outputs`:

```
{
  unit_economics_strategy, jtbd_strategy, growth_strategy,
  merged_strategies: [...],
  strategy_summary: {total_recommendations, frameworks_applied, consensus_recommendation}
}
```

Also increments `iteration_count` — used by the critic's retry routing.
