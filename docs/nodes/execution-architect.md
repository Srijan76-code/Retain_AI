# Node 12 — `execution_architect`

**File:** [`backend/app/graph/nodes/execution_architect.py`](../../backend/app/graph/nodes/execution_architect.py) · **Terminal node (→ END).**

## Purpose

Synthesize every earlier artefact (root causes, strategies, simulations, constraints, critic feedback) into the final retention playbook the UI renders.

## Model

Groq `llama-3.3-70b-versatile`, key `GROQ_API_KEY_3`, temperature 0.3.

## Structured output

Strict nested Pydantic schema — see the file for the full tree. Top-level shape:

```
Playbook {
  title,
  executive_summary { total_problems_identified, total_projected_retention_lift, estimated_timeline, estimated_budget, confidence_level },
  problems_and_solutions [ { priority, problem, solution, retention_impact, implementation_steps [...] } ],
  30_60_90_roadmap { phase_1_30_days, phase_2_60_days, phase_3_90_days },
  success_metrics [...],
  risks_and_mitigations [...],
  resource_requirements { team, technology, budget_breakdown }
}
```

The `30_60_90_roadmap` key uses a Pydantic alias (field name `roadmap_30_60_90` → alias `30_60_90_roadmap`) because Python identifiers can't start with a digit.

## De-duplication pass

Post-LLM, identical-looking problems are merged:

- Title word overlap > 60% → duplicate
- Solution `key_actions` overlap > 50% → duplicate

Priorities are renumbered after dedup.

## Enrichment

Adds `created_date`, `company` (from questionnaire industry), `estimated_total_lift` (from `lift_percent`).

## SSE event

Emits `{type: "solution_ready", data: {final_playbook}}` followed by `{type: "complete"}`. The UI's "Playbook" tab renders `final_playbook`.

## Failure mode

On LLM failure, writes `final_playbook: {error}` and `playbook_status: "error"`. The frontend shows a retry affordance.
