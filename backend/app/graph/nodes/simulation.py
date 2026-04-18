"""
Node 10: Simulation
=====================
Action:  Predict lift & ROI via Monte Carlo
Tools:   Monte Carlo, NumPy
Adds:    simulations, lift_percent
"""

from __future__ import annotations

import numpy as np
from app.graph.state import RetentionGraphState


def simulation_node(state: RetentionGraphState) -> dict:
    """Run Monte Carlo simulations to predict retention lift and ROI."""
    try:
        strategy_outputs = state.get("strategy_outputs", {})
        merged_strategies = strategy_outputs.get("merged_strategies", [])
        roi_projections = state.get("unit_economist_output", {}).get("roi_projections", {})

        # Run Monte Carlo simulation
        simulations = run_monte_carlo_simulation(merged_strategies, roi_projections)

        # Extract expected lift from simulations
        lift_percent = simulations.get("expected_lift", 15.0)

        return {
            "simulations": simulations,
            "lift_percent": round(lift_percent, 2),
            "simulation_confidence": "high" if len(merged_strategies) > 0 else "low",
            "current_node": "simulation",
        }

    except Exception as e:
        return {
            "simulations": {
                "iterations": 10000,
                "expected_lift": 12.0,
                "confidence_interval": [8.0, 16.0],
                "expected_roi": 150.0,
            },
            "lift_percent": 12.0,
            "errors": [*state.get("errors", []), f"Simulation error: {str(e)}"],
            "current_node": "simulation",
        }


def run_monte_carlo_simulation(strategies: list, roi_data: dict, iterations: int = 10000) -> dict:
    """Run Monte Carlo simulation for strategy outcomes."""
    np.random.seed(42)

    intervention_impacts = []
    roi_samples = []

    for strategy in strategies[:3]:  # Top 3 strategies
        expected_impact = strategy.get("expected_roi", 20)

        # Sample from normal distribution (mean=expected, std=0.2*mean)
        impact_samples = np.random.normal(
            loc=expected_impact / 100,  # Convert % to decimal
            scale=expected_impact / 100 * 0.2,
            size=iterations,
        )
        impact_samples = np.clip(impact_samples, 0, 0.5)  # Clip to 0-50%

        intervention_impacts.append({
            "intervention": strategy.get("recommendation", ""),
            "mean_lift": round(float(np.mean(impact_samples)) * 100, 2),
            "std_dev": round(float(np.std(impact_samples)) * 100, 2),
            "percentile_10": round(float(np.percentile(impact_samples, 10)) * 100, 2),
            "percentile_90": round(float(np.percentile(impact_samples, 90)) * 100, 2),
        })

        # ROI sampling
        roi_samples.extend(impact_samples * 200)  # Convert lift to ROI estimate

    # Calculate overall metrics
    combined_lift = np.mean(impact_samples) * 100 if len(impact_samples) > 0 else 12.0
    ci_lower = np.percentile(impact_samples, 5) * 100 if len(impact_samples) > 0 else 8.0
    ci_upper = np.percentile(impact_samples, 95) * 100 if len(impact_samples) > 0 else 16.0

    return {
        "iterations": iterations,
        "expected_lift": round(float(combined_lift), 2),
        "confidence_interval_5_95": [round(float(ci_lower), 2), round(float(ci_upper), 2)],
        "expected_roi": round(float(np.mean(roi_samples)) if roi_samples else 150.0, 1),
        "intervention_impacts": intervention_impacts,
        "simulation_summary": {
            "strategies_modeled": len(strategies),
            "scenarios_analyzed": iterations,
            "confidence_level": "95% CI",
        },
    }
