# Node 11 — `strategy_critic`

**File:** [`backend/app/graph/nodes/strategy_critic.py`](../../backend/app/graph/nodes/strategy_critic.py)

## Purpose

Senior-partner-style review of the proposed strategy. Produces a quality score, strengths/weaknesses, constraint-violation count, and a final verdict that gates `execution_architect`.

## Model

Groq `llama-3.3-70b-versatile`, key `GROQ_API_KEY_2`, temperature 0.1 (deliberately cold — critique should be consistent).

## Verdict logic

LLM returns `verdict ∈ {approved, low_lift, violation}`. Final verdict is adjusted by hard thresholds:

```python
if llm_verdict == "approved" and quality_score >= 0.55 and lift_percent >= 8:
    critic_verdict = "approved"
elif evaluation.constraint_violations > 0 or llm_verdict == "violation":
    critic_verdict = "violation"
else:
    critic_verdict = "low_lift"
```

## Routing

`route_after_strategy_critic`:

| Verdict | Next |
|---|---|
| `approved` | `execution_architect` |
| `low_lift` or `violation` | loop back to `adaptive_hitl` (unless `iteration_count >= MAX_CRITIC_ITERATIONS`, currently `0` — effectively always forwards) |

## Output

```
critic_verdict: "approved" | "low_lift" | "violation"
iteration_count: <incremented>
criticism: {quality_score, lift_assessment, constraint_violations, critical_feedback, strengths, weaknesses, recommendations}
feedback: <verdict_reason string>
```

`criticism` is later included in the `execution_architect` prompt so the final playbook reflects the critique.
