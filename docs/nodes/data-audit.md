# Node 2 — `data_audit`

**File:** [`backend/app/graph/nodes/data_audit.py`](../../backend/app/graph/nodes/data_audit.py)

## Purpose

Compute a single `data_quality_score` in `[0, 1]` and log what was checked. The conditional edge after this node routes to `feature_engineering` if score ≥ `DATA_QUALITY_THRESHOLD` (0.5), else to [`retry_handler`](./retry-handler.md).

## Scoring

```
null_penalty = max_null_pct_any_column / 100 * 0.3
dup_penalty  = min(dup_count / row_count, 0.2)
size_penalty = 0 if row_count >= 50 else (1 - row_count/50) * 0.2
score        = max(0, 1 - null_penalty - dup_penalty - size_penalty)
```

Threshold and loop cap live in [`backend/app/graph/conditions.py`](../../backend/app/graph/conditions.py):

```python
DATA_QUALITY_THRESHOLD = 0.5
MAX_RETRIES = 0   # currently one-shot — no retry loop
```

## Inputs

`raw_csv_path`.

## Outputs

| Key | Shape |
|---|---|
| `data_quality_score` | float |
| `data_quality_logs` | `list[str]` — human-readable lines |
| `quality_metrics` | `{null_percentages, duplicates, row_count, column_count, dtypes}` |

## Why it re-reads the CSV

Every data node re-reads via DuckDB rather than using `state["normalized_df"]`. This trades a little I/O for resilience against serialization drift and keeps nodes independently runnable.
