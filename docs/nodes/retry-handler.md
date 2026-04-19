# Node — `retry_handler`

**File:** [`backend/app/graph/nodes/retry_handler.py`](../../backend/app/graph/nodes/retry_handler.py)

## Purpose

Fallback branch when `data_audit` scores below threshold. Builds a human-readable message listing detected issues (missing values, duplicates, size) and a suggestion list. The conditional edge `route_after_retry` then either loops back to `input_ingest` (if `retry_count < MAX_RETRIES`) or proceeds to `feature_engineering` with whatever data exists.

## Outputs

| Key | Shape |
|---|---|
| `retry_count` | int, incremented |
| `status` | `AWAITING_USER_DATA` / `FAILED_MAX_RETRIES` / `ERROR` |
| `user_message` | string with issues and attempt count |
| `user_action` | short next-step string |
| `suggestion` | top 3 suggestions from `generate_data_quality_suggestions()` |

## Loop behaviour

`MAX_RETRIES = 0` in [`conditions.py`](../../backend/app/graph/conditions.py) — the loop is currently disabled, so this node always forwards to `feature_engineering`. Raising that constant turns on iterative data-quality retries.
