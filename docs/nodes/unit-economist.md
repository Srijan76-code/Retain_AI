# Node 9a — `unit_economist`

**File:** [`backend/app/graph/nodes/unit_economist_node.py`](../../backend/app/graph/nodes/unit_economist_node.py) → [`backend/app/graph/agents/execution/unit_economist.py`](../../backend/app/graph/agents/execution/unit_economist.py).

## Purpose

Apply an LTV/CAC lens: propose interventions with ROI, payback period, and LTV lift for each verified root cause.

## Model

Groq `llama-3.3-70b-versatile`, key `GROQ_API_KEY_1`, temperature 0.3.

## Output

`unit_economist_output`:

```
{
  agent: "unit_economist",
  proposed_interventions: [{intervention, confidence, estimated_cost, cost_usd, expected_roi, rationale}],
  roi_projections: { cause: {year_1_revenue_impact, implementation_cost, roi_percent, payback_months} },
  cac_ltv_impact: { cause: {current_ltv, projected_ltv, ltv_improvement_pct} },
  cost_estimates: { cause: {implementation, ongoing_monthly, time_to_value_weeks} },
  top_roi_intervention: { intervention, expected_roi },
  framework: "Unit Economics / LTV-CAC",
  confidence: <avg of intervention confidences>
}
```

## Consumed by

- [`strategy_merge`](./strategy-merge.md) — pulls `top_roi_intervention` or first intervention into `merged_strategies`
- [`simulation`](./simulation.md) — uses `roi_projections`
- [`execution_architect`](./execution-architect.md) — passes full output into the final playbook prompt

## Deep dive

[`docs/agents/unit-economist.md`](../agents/unit-economist.md).
