# Node 10 — `simulation`

**File:** [`backend/app/graph/nodes/simulation.py`](../../backend/app/graph/nodes/simulation.py)

## Purpose

Monte Carlo sampling over the top-3 merged strategies to estimate expected retention lift and a 5th/95th percentile confidence band.

## Model

```python
np.random.seed(42)
for strategy in strategies[:3]:
    impact_samples = np.random.normal(
        loc=expected_impact / 100,
        scale=expected_impact / 100 * 0.2,   # std = 20% of mean
        size=10000,
    )
    impact_samples = np.clip(impact_samples, 0, 0.5)
```

Per-strategy: `mean_lift`, `std_dev`, `percentile_10`, `percentile_90`. Overall: `expected_lift`, `confidence_interval_5_95`, `expected_roi` (lift × 200 heuristic).

## Output

```
simulations: {
  iterations: 10000,
  expected_lift, confidence_interval_5_95, expected_roi,
  intervention_impacts: [...per strategy...],
  simulation_summary: {strategies_modeled, scenarios_analyzed, confidence_level: "95% CI"}
}
lift_percent: <expected_lift>
```

## Why the seed is fixed

Deterministic results for the same input, so repeat runs of the pipeline on the same CSV produce identical lift figures — easier to debug and easier for the critic's threshold (`lift ≥ 8%`) to reason about.
