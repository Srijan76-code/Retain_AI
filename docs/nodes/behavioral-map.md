# Node 4 — `behavioral_map`

**File:** [`backend/app/graph/nodes/behavioral_map.py`](../../backend/app/graph/nodes/behavioral_map.py)

## Purpose

Fit a **Kaplan-Meier** survival estimator on the population and derive the artefacts the UI's churn card consumes: survival curve, median survival time, retention at standard business milestones, and tenure-based cohort splits.

## KM fit

```python
kmf = KaplanMeierFitter()
kmf.fit(durations=tenure_col, event_observed=churn_col, label="retention")
```

`event_observed=1` means the user churned, `0` means censored (still active). If the CSV has no churn label, all rows are treated as observed.

## Downsampling for the frontend

The full `kmf.survival_function_` can have hundreds of steps. The node downsamples to at most 20 roughly-evenly-spaced points and always includes the final point:

```python
step = max(1, len(times) // 20)
sampled_indices = list(range(0, len(times), step))
if sampled_indices[-1] != len(times) - 1:
    sampled_indices.append(len(times) - 1)
```

## Outputs

`behavior_curves`:

| Key | Shape |
|---|---|
| `survival_curve` | `{ "month_1": 0.95, "month_2": 0.91, ... }` |
| `retention_by_period` | legacy alias of `survival_curve` |
| `churn_probability` | `1 - km_at_final_time` |
| `max_tenure` | last observed time |
| `median_survival_time` | `kmf.median_survival_time_` (int or `None` if ∞) |
| `milestone_retention` | retention at months `[1, 3, 6, 12, 24, 36]` (nearest-lower KM point) |

`behavior_cohorts`: three cohorts (`low_tenure`, `medium_tenure`, `high_tenure`) split at the p25 and p75 of the tenure column. Each has `size`, `retention_rate` (computed from the real churn column), and `tenure_range: {min, max}`.

## Frontend consumption

- The churn probability **slider** uses `parseSurvivalCurve` + `getChurnAtPeriod` (nearest-lower lookup) in [`frontend/app/results/[job_id]/page.tsx`](../../frontend/app/results/[job_id]/page.tsx) to turn the survival curve into a live `X% by month Y` readout.
- The milestone strip displays `milestone_retention` color-coded: green ≥80%, yellow ≥60%, red below.
- The "Median Survival" card displays `median_survival_time`.

## SSE event

Emits `{type: "churn_profile_ready"}` carrying `churn_probability`, `survival_curve`, `max_tenure`, `median_survival_time`, `milestone_retention`, and `behavior_cohorts`.

## Fan-out

After this node the graph fans out to `forensic_detective` **and** `pattern_matcher` in parallel.
