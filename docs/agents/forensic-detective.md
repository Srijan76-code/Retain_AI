# Agent — Forensic Detective

**File:** [`backend/app/graph/agents/discovery/forensic_detective.py`](../../backend/app/graph/agents/discovery/forensic_detective.py)

Discovery-pod agent. Uses dataset statistics + RAG-retrieved frameworks to diagnose root causes with citations.

## Model

| | |
|---|---|
| Provider | Google Gemini |
| Model ID | `gemini-3-flash-preview` |
| Temp | `0.3` |
| API key | `GOOGLE_API_KEY_1` |
| Structured output | via `safe_llm_invoke` (`utils.py`) with fallback JSON parsing |

## Pydantic schema

```python
class DetectiveResult(BaseModel):
    suspected_causes: List[str]
    confidence_scores: Dict[str, float]
    citations: Dict[str, List[str]] = Field(default_factory=dict)
```

## Data pass

1. Re-reads CSV with DuckDB.
2. Computes:
   - overall `churn_rate`
   - `churn_by_channel` — breaks down churn by any column matching `acquisition` / `channel`
   - `churn_by_integration` — by any column matching `integration`
3. Passes `stats + behavior_curves` through `_derive_signals()` to get semantic tags (see [`docs/nodes/forensic-detective.md`](../nodes/forensic-detective.md) for the full tag table).

## RAG retrieval

```python
rag_query = f"Root causes of churn with patterns: {signals}. Churn rate {x}%. Median survival {m}."
retrieved = rag_retrieve(rag_query, k=5, signals=signals)
```

Top-5 chunks are concatenated into `evidence_block` and injected into the prompt.

## Prompt contract

```
You are a B2B SaaS retention analyst. Diagnose the 3 most likely root causes of churn.

── Dataset statistics ── ...
── Retrieved retention frameworks ── <evidence_block>

Requirements:
- Each root cause must be specific and grounded in one or more retrieved frameworks above.
- Reference the framework by its source id in the `citations` map.
- Confidence in [0.7, 1.0].
```

## Output shape

```
{
  agent: "forensic_detective",
  suspected_causes: [...],
  confidence_scores: { cause: 0.85, ... },
  citations: { cause: ["reforge_aha_001", ...], ... },
  retrieved_sources: [{id, source, topic, score}, ...],
  statistical_evidence: {churn_rate, churn_by_channel, churn_by_integration},
  analysis_depth: "high"
}
```

## Failure modes

| Failure | Observable |
|---|---|
| CSV missing / DuckDB parse error | returns `{agent, error}` — the whole agent output is an error stub |
| Chroma collection empty | `evidence_block = "(no retrieved frameworks — reason from stats alone)"`, no citations |
| LLM returns invalid JSON | `safe_llm_invoke` raises `ValueError` → caught, returns `{error}` |
| LLM returns `confidence < 0.7` | no guard — low scores can still pass through to `hypothesis_validation`'s threshold |
