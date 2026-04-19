# Node 1 — `input_ingest`

**File:** [`backend/app/graph/nodes/input_ingest.py`](../../backend/app/graph/nodes/input_ingest.py) · **Entry point of the graph.**

## Purpose

Load the raw CSV into a DataFrame and detect which columns represent customer ID, tenure, usage, support, plan, and churn. Every downstream node relies on `input_context.detected_columns` to find the right columns, so this is the single source of truth for schema.

## Inputs (state)

| Key | Source |
|---|---|
| `raw_csv_path` | POST body |
| `questionnaire` | POST body (form payload) |

## Outputs (state)

| Key | Shape |
|---|---|
| `raw_csv_path` | resolved absolute path (re-written so downstream nodes don't depend on `cwd`) |
| `normalized_df` | `list[dict]` — `df.to_dict(orient="records")` |
| `input_context` | `{source, row_count, column_count, detected_columns, business_context, industry, company_size}` |
| `input_constraints` | `{time_range, product_lines, market_segment, budget_constraints, legal_constraints}` |
| `retry_count` | propagated |

## Column detection

Case-insensitive substring match on column names:

| Field | Matches |
|---|---|
| `customer_id` | `id`, `user` |
| `tenure` | `tenure`, `months_active`, `months` |
| `usage` | `usage`, `logins` |
| `support` | `support`, `tickets` |
| `plan` | `plan`, `contract` |
| `churn` | via `get_churn_column()` — requires binary `{0,1}` column whose name contains `churn` |

`get_churn_column` lives in [`backend/app/graph/utils.py`](../../backend/app/graph/utils.py).

## Failure mode

On exception: appends to `errors`, increments `retry_count`. Does not raise — the graph continues so `data_audit` can score whatever was loaded (if anything).

## Called by

Entry point (`graph.set_entry_point("input_ingest")`). Also re-entered from [`retry_handler`](./retry-handler.md) when data quality fails.
