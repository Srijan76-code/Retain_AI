# Node 9b — `jtbd_specialist`

**File:** [`backend/app/graph/nodes/jtbd_specialist_node.py`](../../backend/app/graph/nodes/jtbd_specialist_node.py) → [`backend/app/graph/agents/execution/jtbd_specialist.py`](../../backend/app/graph/agents/execution/jtbd_specialist.py).

## Purpose

Apply the Jobs-to-be-Done framework: for each verified root cause, identify the functional/emotional/social job being underserved, quantify the satisfaction gap, and propose interventions that close it.

## Model

Groq `llama-3.3-70b-versatile`, key `GROQ_API_KEY_1`, temperature 0.5 — slightly warmer than unit economist because JTBD benefits from qualitative framing.

## Output

`jtbd_specialist_output`:

```
{
  agent: "jtbd_specialist",
  identified_jobs: [{job_type, description, related_cause}],
  satisfaction_gaps: [{job, current_satisfaction, target_satisfaction, gap}],
  proposed_interventions: [{intervention, job_focus, expected_impact, implementation_effort, confidence}],
  job_priority_ranking: [{job_type, description, priority}],
  framework: "Jobs-to-be-Done",
  confidence: <avg>
}
```

## Deep dive

[`docs/agents/jtbd-specialist.md`](../agents/jtbd-specialist.md).
