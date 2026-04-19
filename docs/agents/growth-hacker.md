# Agent — Growth Hacker

**File:** [`backend/app/graph/agents/execution/growth_hacker.py`](../../backend/app/graph/agents/execution/growth_hacker.py)

Strategy-pod agent. Designs AARRR-style activation experiments and viral loops.

## Model

| | |
|---|---|
| Provider | Groq |
| Model ID | `llama-3.3-70b-versatile` |
| Temp | `0.6` (warmest of the three strategy agents) |
| API key | `GROQ_API_KEY_2` |

## Pydantic schema

```python
class GrowthHackerResult(BaseModel):
    proposed_tactics: List[ProposedTactic]
    experiment_designs: List[ExperimentDesign]     # {test_name, control, variant, metric, sample_size, duration_days}
    activation_improvements: List[ActivationImprovement]
    viral_loops: List[ViralLoop]
    speed_to_impact: SpeedToImpact                 # {quick_wins, medium_term, long_term, prioritization_logic}
```

`ProposedTactic.confidence` defaults to `0.8`.

## Inputs

- `verified_root_causes`
- `constrained_brief`

## Prompt

```
As a Growth Hacker, design high-impact activation and retention experiments
for a B2B SaaS product.

Focus on the Pirate Metrics (AARRR) framework — specifically Activation
and Retention loops.
```

## Output

See [`docs/nodes/growth-hacker.md`](../nodes/growth-hacker.md).

## Why the warmer temperature

Experiment design benefits from variance — the critic downstream is cold (0.1) and will kill anything that doesn't hold up. Creative exploration at this stage is the point.

## Failure mode

Error stub `{agent, error}`. The merged strategies list loses the experiment-design framework; `simulation` still runs over whatever strategies remain.
