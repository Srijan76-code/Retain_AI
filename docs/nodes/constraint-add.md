# Node 7 — `constraint_add`

**File:** [`backend/app/graph/nodes/constraint_add.py`](../../backend/app/graph/nodes/constraint_add.py)

## Purpose

Filter verified root causes against the real-world constraints the user provided in the questionnaire (budget, legal). Produce a ranked list of feasible interventions and a count of constraints actually applied.

## Intervention cost heuristic

Pure-Python keyword match on the cause text:

| If cause contains... | cost |
|---|---|
| `cheap`, `feature adoption` | `low` |
| `pricing`, `support` | `medium` |
| anything else | `high` |

Then:

- `budget == "low"` blocks `medium` + `high`
- `budget == "medium"` blocks `high`
- any `legal_constraint` containing `gdpr` blocks causes containing `tracking` (`"Requires legal review"`)

## Output

`constrained_brief`:

```
{
  verified_causes, applied_constraints, feasible_interventions,
  priority_ranking: [{rank, intervention, impact_score}, ...top 5],
  constraint_summary: {total_constraints_applied, causes_eliminated, feasible_count},
  business_context
}
```

Ranking key: `confidence × (1.0 if low-cost else 0.8)`, descending.

## Why pure Python

Deterministic filtering with business rules — an LLM here adds variance without adding value. The LLM re-enters the pipeline at the strategy pod.
