# Node 5c — `diagnosis_merge`

**File:** [`backend/app/graph/nodes/diagnosis_merge.py`](../../backend/app/graph/nodes/diagnosis_merge.py)

Fan-in after the two parallel discovery nodes.

## Purpose

1. Run the **Professional Skeptic** ([`docs/agents/professional-skeptic.md`](../agents/professional-skeptic.md)) on the forensic + pattern outputs to produce counter-arguments, bias flags, and robustness scores.
2. Build `merged_hypotheses` from the forensic detective's top-3 causes, preserving each cause's confidence and citations.

## merged_hypotheses shape

```
{
  hypothesis: "<cause string>",
  confidence: <float from forensic>,
  supported_by: ["forensic_detective", "pattern_matcher"]
}
```

> Note: the wired node file (`diagnosis_merge.py`) builds the simpler shape above; the unused `diagnosis_pod.py` contains an enriched variant that also attaches `citations: [{id, source}]` per hypothesis. Citations remain available via `state["forensic_detective_output"]["citations"]` regardless.

## Outputs

- `professional_skeptic_output` — skeptic results
- `diagnosis_results` — `{forensic_findings, pattern_findings, skeptic_findings, merged_hypotheses, highest_confidence, total_patterns_identified}`
- `discovery_attempts` — incremented (used by retry routing)

## SSE event

Emits `{type: "diagnosis_ready"}` carrying `merged_hypotheses`. Frontend renders these as "Root Cause" cards.

## Next

→ [`hypothesis_validation`](./hypothesis-validation.md) applies a confidence × robustness gate.
