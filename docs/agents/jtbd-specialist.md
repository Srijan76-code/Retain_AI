# Agent — JTBD Specialist

**File:** [`backend/app/graph/agents/execution/jtbd_specialist.py`](../../backend/app/graph/agents/execution/jtbd_specialist.py)

Strategy-pod agent. Applies the Jobs-to-be-Done framework: every root cause is reframed as an underserved functional/emotional/social job.

## Model

| | |
|---|---|
| Provider | Groq |
| Model ID | `llama-3.3-70b-versatile` |
| Temp | `0.5` |
| API key | `GROQ_API_KEY_1` |

## Pydantic schema

```python
class JTBDResult(BaseModel):
    identified_jobs: List[IdentifiedJob]         # {job_type, description, related_cause}
    satisfaction_gaps: List[SatisfactionGap]     # {job, current, target, gap}
    proposed_interventions: List[ProposedIntervention]
    job_priority_ranking: List[JobPriority]
```

`ProposedIntervention.confidence` defaults to `0.8` so the Pydantic parse doesn't fail when the LLM omits it.

## Inputs

- `verified_root_causes`
- `constrained_brief`

## Prompt excerpt

```
For each cause, identify:
1. Functional job (what does the user need to accomplish?)
2. Emotional job (how should they feel?)
3. Social job (how should they be perceived?)

Then propose interventions that address the most critical jobs.
```

## Output

See [`docs/nodes/jtbd-specialist.md`](../nodes/jtbd-specialist.md).

## Failure mode

Error stub `{agent, error}`. `strategy_merge` skips this framework and the merged strategies will be shorter.
