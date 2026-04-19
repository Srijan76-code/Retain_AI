# Node 5b — `pattern_matcher`

**File:** [`backend/app/graph/nodes/pattern_matcher_node.py`](../../backend/app/graph/nodes/pattern_matcher_node.py) → [`backend/app/graph/agents/discovery/pattern_matcher.py`](../../backend/app/graph/agents/discovery/pattern_matcher.py).

Runs in parallel with [`forensic_detective`](./forensic-detective.md).

## Purpose

Looks at `feature_store` and `behavior_cohorts` (not the raw CSV) and asks Gemini 3 Flash to identify:

- High-risk segments
- Feature-adoption gaps
- Churn sequences (`step1 → step2 → churn` with probabilities)
- Topic clusters

## Output

`pattern_matcher_output`:

```
{
  agent: "pattern_matcher",
  patterns_found: [{pattern, churn_risk, affected_users, description}, ...],
  user_segments: [{segment_id, size, retention_rate, characteristics}, ...],
  topic_clusters: [{topic, cluster_size}, ...],
  churn_sequences: [{sequence, probability}, ...],
  pattern_confidence: 0.XX
}
```

## Why it's LLM-only (no stats pass)

Unlike `forensic_detective`, this node trusts the aggregated state written by earlier nodes rather than re-reading the CSV. It's intentionally the "creative" counterpart to forensic's evidence-grounded reasoning — the Professional Skeptic then stress-tests both in `diagnosis_merge`.

## Deep dive

[`docs/agents/pattern-matcher.md`](../agents/pattern-matcher.md).
