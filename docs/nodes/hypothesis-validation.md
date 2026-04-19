# Node 6 — `hypothesis_validation`

**File:** [`backend/app/graph/nodes/hypothesis_validation.py`](../../backend/app/graph/nodes/hypothesis_validation.py)

## Purpose

Gate each merged hypothesis by combining the forensic agent's `confidence` with the skeptic's `robustness_scores`.

## Gate logic

```
if confidence > 0.50 and robustness > 0.35: evidence = "Statistical validation passed"
elif confidence > 0.35:                     evidence = "Weak statistical support"
else:                                       dropped
```

`hypothesis_status` is set to `"verified"` if at least one hypothesis passes the strong gate, `"weak_proof"` if any pass the weak gate, else `"unverified"`.

## Routing

`route_after_hypothesis_validation` in [`conditions.py`](../../backend/app/graph/conditions.py):

- `verified` → `constraint_add`
- otherwise → loop back to `behavioral_map` (unless `discovery_attempts >= MAX_DISCOVERY_ATTEMPTS`, which is `0` today — effectively always forwards).

## Output

`verified_root_causes: [{cause, confidence, robustness, evidence, p_value, recommendation}, ...]`

`validation_metrics: {hypotheses_tested, hypotheses_verified, validation_quality}`

The downstream strategy agents all read `verified_root_causes` as their primary input.
