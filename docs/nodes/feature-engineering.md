# Node 3 — `feature_engineering`

**File:** [`backend/app/graph/nodes/feature_engineering.py`](../../backend/app/graph/nodes/feature_engineering.py)

## Purpose

Compute retention-relevant features: RFM z-scores, LTV aggregates, engagement velocity, engagement cohorts, and — most importantly — a **Cox Proportional Hazards** survival model that identifies currently-active users with the shortest predicted remaining lifetime.

## Feature bundles

| Bundle | Source column | Notes |
|---|---|---|
| `rfm_scores` | tenure / usage / ltv | mean + std z-scores |
| `velocity_metrics` | usage | mean logins/month, low-engagement threshold at p25 |
| `ltv_estimates` | any column matching `ltv`, `revenue`, `monetary`, `value` | mean + median |
| `engagement_cohorts` | usage | p25/p50/p75 split |
| `predictive_churn_risk` | all numeric cols | CoxPHFitter from `lifelines` |

## Predictive churn risk (CoxPH)

```python
cph = CoxPHFitter(penalizer=0.1)
cph.fit(df_ml, duration_col=tenure_col, event_col=churn_col)
median_survival_times = cph.predict_median(X_active)
expected_remaining_time = median_survival_times - current_tenures
high_risk = expected_remaining_time < 6        # fewer than 6 tenure units left
```

Stores `total_active_evaluated`, `high_risk_customers_count`, `risk_segment_pct`, `concordance_index` (model quality), `lowest_forecasted_survival_time`.

## Why it runs before `behavioral_map`

`behavioral_map` provides population-level KM curves; this node provides the per-user risk score. Both run on the same CSV but serve different UI cards — the "risk_ready" SSE event is fired right after this node.

## Failure mode

If CoxPH can't converge (insufficient variance, too few rows, or single-class churn), the block is wrapped in try/except and writes `predictive_churn_risk: {error: ...}` — the rest of the feature store still gets populated.

## SSE event

After this node the backend emits `{type: "risk_ready"}` with `{high_risk_count, total_active, risk_pct, confidence, insight, has_model}`.
