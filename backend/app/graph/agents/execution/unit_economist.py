"""
Execution Agent: Unit Economist
=================================
Analyses unit economics implications.
Called by: strategy_pod_node
"""

from __future__ import annotations

from typing import Any
from app.graph.state import RetentionGraphState


def run_unit_economist(state: RetentionGraphState) -> dict[str, Any]:
    """Generate strategies optimised for unit economics."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        constrained_brief = state.get("constrained_brief", {})
        feature_store = state.get("feature_store", {})

        # Extract LTV proxy if available
        ltv_proxy = feature_store.get("ltv_estimates", {}).get("ltv_proxy", 1000)

        proposed_interventions = []
        roi_projections = {}
        cac_ltv_impact = {}
        cost_estimates = {}

        # For each cause, estimate economic impact
        feasible_interventions = constrained_brief.get("feasible_interventions", [])

        for intervention in feasible_interventions[:3]:
            cause = intervention.get("cause", "")
            confidence = intervention.get("confidence", 0.5)
            cost = intervention.get("estimated_cost", "medium")

            # Map cost to $ amount
            cost_map = {"low": 5000, "medium": 25000, "high": 100000}
            implementation_cost = cost_map.get(cost, 25000)

            # Estimate lift from confidence
            retention_lift_pct = confidence * 30  # Assume 30% max lift

            # Calculate ROI
            additional_retained = 100 * (retention_lift_pct / 100)  # Mock users
            revenue_impact = additional_retained * ltv_proxy
            roi = ((revenue_impact - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0

            proposed_interventions.append({
                "intervention": cause,
                "confidence": confidence,
                "estimated_cost": cost,
                "cost_usd": implementation_cost,
                "expected_roi": round(roi, 1),
            })

            roi_projections[cause] = {
                "year_1_revenue_impact": round(revenue_impact, 0),
                "implementation_cost": implementation_cost,
                "roi_percent": round(roi, 1),
                "payback_months": round(implementation_cost / (revenue_impact / 12), 1) if revenue_impact > 0 else 999,
            }

            # CAC/LTV impact
            current_ltv = ltv_proxy
            new_ltv = current_ltv * (1 + retention_lift_pct / 100)
            cac_ltv_impact[cause] = {
                "current_ltv": round(current_ltv, 2),
                "projected_ltv": round(new_ltv, 2),
                "ltv_improvement_pct": round((new_ltv - current_ltv) / current_ltv * 100, 1),
                "ltv_ratio_improvement": round((new_ltv / current_ltv - 1) * 100, 1),
            }

            cost_estimates[cause] = {
                "implementation": implementation_cost,
                "ongoing_monthly": round(implementation_cost / 12, 0),
                "time_to_value_weeks": 4 + int(cost) == "high" and 4 or 2,
            }

        # Rank by ROI
        proposed_interventions.sort(key=lambda x: x.get("expected_roi", 0), reverse=True)

        return {
            "agent": "unit_economist",
            "proposed_interventions": proposed_interventions,
            "roi_projections": roi_projections,
            "cac_ltv_impact": cac_ltv_impact,
            "cost_estimates": cost_estimates,
            "top_roi_intervention": proposed_interventions[0] if proposed_interventions else {},
            "framework": "Unit Economics / LTV-CAC",
            "confidence": 0.65,
        }

    except Exception as e:
        return {
            "agent": "unit_economist",
            "proposed_interventions": [],
            "roi_projections": {},
            "cac_ltv_impact": {},
            "cost_estimates": {},
            "error": str(e),
        }
