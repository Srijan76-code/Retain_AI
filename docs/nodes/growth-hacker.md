# Node 9c — `growth_hacker`

**File:** [`backend/app/graph/nodes/growth_hacker_node.py`](../../backend/app/graph/nodes/growth_hacker_node.py) → [`backend/app/graph/agents/execution/growth_hacker.py`](../../backend/app/graph/agents/execution/growth_hacker.py).

## Purpose

Design AARRR-style experiments and activation improvements: specific A/B tests with sample sizes, durations, control/variant descriptions, and viral loops.

## Model

Groq `llama-3.3-70b-versatile`, key `GROQ_API_KEY_2`, temperature 0.6 — the warmest strategy agent, because the output is supposed to include creative experiment designs.

## Output

`growth_hacker_output`:

```
{
  agent: "growth_hacker",
  proposed_tactics: [{name, description, target_metric, expected_lift, implementation_timeline, confidence}],
  experiment_designs: [{test_name, control, variant, metric, sample_size, duration_days}],
  activation_improvements: [{focus, current_step, improvement, estimated_lift}],
  viral_loops: [{loop, trigger, incentive, estimated_impact}],
  speed_to_impact: {quick_wins, medium_term, long_term, prioritization_logic},
  framework: "Pirate Metrics (AARRR)",
  confidence: <avg>
}
```

## Deep dive

[`docs/agents/growth-hacker.md`](../agents/growth-hacker.md).
