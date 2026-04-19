# Agent — Pattern Matcher

**File:** [`backend/app/graph/agents/discovery/pattern_matcher.py`](../../backend/app/graph/agents/discovery/pattern_matcher.py)

Discovery-pod agent. LLM-only — reads the aggregated state (not the raw CSV) and identifies high-risk segments and churn sequences.

## Model

| | |
|---|---|
| Provider | Google Gemini |
| Model ID | `gemini-3-flash-preview` |
| Temp | `0.2` |
| API key | `GOOGLE_API_KEY_2` |

## Pydantic schema

```python
class PatternMatcherResult(BaseModel):
    patterns_found: List[PatternDef]
    user_segments: List[UserSegment]
    topic_clusters: List[TopicCluster]
    churn_sequences: List[ChurnSequence]
    pattern_confidence: float
```

## Inputs (from state)

- `feature_store` — RFM, LTV, velocity, engagement cohorts, CoxPH risk model output
- `behavior_cohorts` — `low/medium/high_tenure` with retention rates

## Prompt

```
Analyze these user behavior cohorts and features to identify recurring
churn patterns and segments.

Identify:
1. High-risk user segments.
2. Feature-based patterns (e.g., specific feature adoption gaps).
3. Common "churn sequences" (steps users take before leaving).
```

## Output

```
{
  agent: "pattern_matcher",
  patterns_found: [{pattern, churn_risk, affected_users, description}],
  user_segments: [{segment_id, size, retention_rate, characteristics}],
  topic_clusters: [{topic, cluster_size}],
  churn_sequences: [{sequence, probability}],
  pattern_confidence: 0.XX
}
```

## Failure modes

Same as forensic detective — malformed JSON or API error returns `{agent, error}`. The `diagnosis_merge` node still proceeds, but the skeptic has less to work with and `total_patterns_identified` drops to 0.

## Why it's intentionally "creative"

Temperature 0.2 is still low but noticeably warmer than no-randomness, and the prompt doesn't force citations. The Professional Skeptic downstream is the corrective — it rates `pattern_quality` and `combined_confidence` that feed into the validation gate.
