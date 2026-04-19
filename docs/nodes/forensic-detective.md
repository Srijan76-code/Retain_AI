# Node 5a — `forensic_detective`

**File:** [`backend/app/graph/nodes/forensic_detective_node.py`](../../backend/app/graph/nodes/forensic_detective_node.py) (thin wrapper) → [`backend/app/graph/agents/discovery/forensic_detective.py`](../../backend/app/graph/agents/discovery/forensic_detective.py) (agent logic).

Runs in parallel with [`pattern_matcher`](./pattern-matcher.md); both merge into [`diagnosis_merge`](./diagnosis-merge.md).

## Purpose

Compute dataset-level churn statistics, translate them into semantic signal tags, retrieve 5 RAG chunks biased toward those signals, then ask Gemini 3 Flash to produce 3 root causes with citations to the retrieved chunks.

## Flow

```
stats (DuckDB) ──► _derive_signals ──► RAG retrieve(k=5, signals)
                                              │
                                              ▼
                                    evidence_block
                                              │
                                              ▼
                                  Gemini 3 Flash (temp 0.3)
                                              │
                                              ▼
                      DetectiveResult { suspected_causes, confidence_scores, citations }
```

## Signal derivation

`_derive_signals(stats, behavior_curves)` in the agent file produces tags like:

| Condition | Signal tag |
|---|---|
| `churn_rate > 0.25` | `high_churn` |
| channel churn spread > 0.15 | `channel_churn`, `channel_variance`, `bad_fit` |
| any integration data | `low_integration`, `integration_failure`, `b2b_churn` |
| `median_survival_time ≤ 3` | `short_tenure_churn`, `30_day_cliff`, `onboarding_friction` |
| `median_survival_time ≤ 9` | `mid_tenure_churn`, `90_day_cliff`, `engagement_decay` |
| `milestone_retention.month_1 < 0.85` | `new_user_drop_off` |

The RAG layer adds `+0.05` per matching signal tag to the cosine-similarity score — see [docs/rag.md](../rag.md).

## Prompt contract

The prompt requires each root cause to cite one or more framework source IDs:

```json
{
  "suspected_causes": ["cause1", "cause2", "cause3"],
  "confidence_scores": { "cause1": 0.85, ... },
  "citations": { "cause1": ["reforge_aha_001"], ... }
}
```

## Output

Written to state under `forensic_detective_output`:

```
{
  agent: "forensic_detective",
  suspected_causes: [...],
  confidence_scores: {...},
  citations: {...},
  retrieved_sources: [{id, source, topic, score}, ...],
  statistical_evidence: {churn_rate, churn_by_channel, churn_by_integration},
  analysis_depth: "high"
}
```

Citations flow through `diagnosis_merge` into each `merged_hypothesis.citations`.

## Deep dive

Full agent reference: [`docs/agents/forensic-detective.md`](../agents/forensic-detective.md).
