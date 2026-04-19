# Agent — Unit Economist

**File:** [`backend/app/graph/agents/execution/unit_economist.py`](../../backend/app/graph/agents/execution/unit_economist.py)

Strategy-pod agent. Maps each verified root cause to an ROI-positive intervention with explicit cost, payback, and LTV lift.

## Model

| | |
|---|---|
| Provider | Groq |
| Model ID | `llama-3.3-70b-versatile` |
| Temp | `0.3` |
| API key | `GROQ_API_KEY_1` |

## Pydantic schema

Nested Pydantic models mirror the JSON contract 1:1 — `UnitEconomistResult` wraps `proposed_interventions`, `roi_projections` (keyed by cause), `cac_ltv_impact` (keyed by cause), `cost_estimates` (keyed by cause), and `top_roi_intervention`.

## Inputs

- `verified_root_causes` (gated by `hypothesis_validation`)
- `constrained_brief` (from `constraint_add`)
- `feature_store.ltv_estimates.ltv_proxy` — defaults to `1000` if absent

## Prompt

```
As a Unit Economist, analyze these churn causes and propose ROI-positive
interventions for a B2B SaaS company.

Focus on:
1. Estimating implementation cost (low/medium/high).
2. Calculating Year-1 ROI based on realistic retention lift.
3. Payback period in months.
```

## Output

See the schema in [`docs/nodes/unit-economist.md`](../nodes/unit-economist.md). `confidence` is the average of each intervention's confidence.

## Failure modes

- Pydantic validation fails on missing fields → `safe_llm_invoke` raises → `{agent, error}` returned, `strategy_merge` silently skips this framework.
- LTV proxy not available → uses `1000` fallback (often produces optimistic ROIs).
