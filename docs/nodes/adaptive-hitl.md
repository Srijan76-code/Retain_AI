# Node 8 — `adaptive_hitl`

**File:** [`backend/app/graph/nodes/adaptive_hitl.py`](../../backend/app/graph/nodes/adaptive_hitl.py)

## Purpose

Generate 2–3 specific, actionable clarifying questions about the top feasible interventions. Structured so a human can answer inline and the answers flow into the strategy agents and critic.

## Model

Gemini 3 Flash (`gemini-3-flash-preview`), key `GOOGLE_API_KEY_2`, temperature 0.3. Pydantic schema `HitlQuestions { questions: List[str] }`.

## Prompt inputs

- top 3 `feasible_interventions` from `constrained_brief`
- `industry` and `company_size` from `input_context`

## Output

```
hitl_questions: [str, str, (str)]
human_clarification: {
  questions_asked: [...],
  responses: {},
  clarification_status: "pending" | "provided"
}
```

`human_clarification.responses` is currently always empty — there is no second UI turn wired in yet. The critic reads whatever is present.

## Fan-out

This node is the fan-out point for the Strategy Pod — it emits edges to all three execution agents in parallel:

- [`unit_economist`](./unit-economist.md)
- [`jtbd_specialist`](./jtbd-specialist.md)
- [`growth_hacker`](./growth-hacker.md)
