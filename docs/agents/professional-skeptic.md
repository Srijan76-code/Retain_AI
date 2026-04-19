# Agent — Professional Skeptic

**File:** [`backend/app/graph/agents/discovery/professional_skeptic.py`](../../backend/app/graph/agents/discovery/professional_skeptic.py)

Called from [`diagnosis_merge`](../nodes/diagnosis-merge.md) — not a standalone node. Adversarial reviewer that stress-tests the other two discovery agents.

## Model

| | |
|---|---|
| Provider | Google Gemini |
| Model ID | `gemini-3-flash-preview` |
| Temp | `0.4` (warmest discovery agent — encourages counter-arguments) |
| API key | `GOOGLE_API_KEY_1` |

## Pydantic schema

```python
class SkepticResult(BaseModel):
    counter_arguments: List[CounterArgument]
    robustness_scores: Dict[str, float]
    alternative_explanations: List[AlternativeExplanation]
    bias_flags: List[BiasFlag]
    overall_quality: OverallQuality
```

## Inputs

Directly passed:

- `forensic_findings.suspected_causes` + `confidence_scores`
- `pattern_findings.churn_sequences` (top 3) + `patterns_found` (top 5)

## Prompt

```
You are a Professional Skeptic reviewing churn analysis findings.
Your job is to challenge assumptions, find flaws, and stress-test hypotheses.

For EACH suspected cause, provide:
1. A specific counter-argument (not generic — reference the actual cause)
2. A robustness score (0.0-1.0) based on how well-supported the hypothesis is
3. One alternative explanation

Also flag any cognitive biases (confirmation bias, survivorship bias, overfitting).
```

## Output

```
{
  agent: "professional_skeptic",
  counter_arguments: [{hypothesis, counter_argument, strength}, ...] (≤5),
  bias_flags: [{issue, risk, recommendation}],
  robustness_scores: { cause: 0.XX, ... },
  alternative_explanations: [{hypothesis, alternative, testability}, ...] (≤3),
  overall_quality_assessment: {forensic_quality, pattern_quality, combined_confidence, recommendation},
  approval_status: "conditional_proceed"
}
```

## How its output is used

`robustness_scores` is the gate in [`hypothesis_validation`](../nodes/hypothesis-validation.md):

```python
if confidence > 0.50 and robustness > 0.35:
    # verified
```

If the skeptic rates a cause low on robustness, that cause cannot reach the "verified" bucket regardless of how confident forensic was.

## Failure mode

Returns `{agent, error}`. Downstream `hypothesis_validation` falls back to `robustness = 0.5` default, so hypotheses with `confidence > 0.50` still pass — the skeptic's absence weakens the gate but doesn't stall the graph.
