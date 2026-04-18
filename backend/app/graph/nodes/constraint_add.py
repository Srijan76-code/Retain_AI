"""
Node 7: Constraint Add
========================
Action:  Reality filtering against business constraints
Tools:   Hard-coded logic
Adds:    constrained_brief
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def constraint_add_node(state: RetentionGraphState) -> dict:
    """Apply real-world constraints to verified root causes."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        input_constraints = state.get("input_constraints", {})
        input_context = state.get("input_context", {})

        # Extract constraints
        budget = input_constraints.get("budget_constraints", "medium")
        legal_constraints = input_constraints.get("legal_constraints", [])
        time_range = input_constraints.get("time_range", "last_12_months")

        applied_constraints = []
        feasible_interventions = []

        # 1. Filter by budget feasibility
        for cause in verified_causes:
            cause_text = cause.get("cause", "")
            confidence = cause.get("confidence", 0)

            # Categorize intervention cost/effort
            if "cheap" in cause_text.lower() or "feature adoption" in cause_text.lower():
                intervention_cost = "low"
            elif "pricing" in cause_text.lower() or "support" in cause_text.lower():
                intervention_cost = "medium"
            else:
                intervention_cost = "high"

            # Check budget
            budget_ok = True
            if budget == "low" and intervention_cost in ["medium", "high"]:
                budget_ok = False
                applied_constraints.append({
                    "constraint": "Budget constraint (low budget)",
                    "cause": cause_text,
                    "outcome": "Eliminated",
                })
            elif budget == "medium" and intervention_cost == "high":
                budget_ok = False

            # 2. Check legal constraints
            legal_ok = True
            for legal_issue in legal_constraints:
                if "gdpr" in legal_issue.lower() and "tracking" in cause_text.lower():
                    legal_ok = False
                    applied_constraints.append({
                        "constraint": f"Legal constraint: {legal_issue}",
                        "cause": cause_text,
                        "outcome": "Requires legal review",
                    })

            # 3. Include if feasible
            if budget_ok and legal_ok and confidence > 0.45:
                feasible_interventions.append({
                    "cause": cause_text,
                    "confidence": confidence,
                    "estimated_cost": intervention_cost,
                    "implementation_timeline": "30-60 days",
                    "expected_lift": round(confidence * 25, 1),  # Estimate
                })

        # Rank by impact potential
        feasible_interventions.sort(
            key=lambda x: x.get("confidence", 0) * (1 if x.get("estimated_cost") == "low" else 0.8),
            reverse=True,
        )

        # Create constrained brief
        constrained_brief = {
            "verified_causes": verified_causes,
            "applied_constraints": applied_constraints,
            "feasible_interventions": feasible_interventions,
            "priority_ranking": [
                {
                    "rank": i + 1,
                    "intervention": interv.get("cause"),
                    "impact_score": round(interv.get("confidence", 0) * 100, 1),
                }
                for i, interv in enumerate(feasible_interventions[:5])
            ],
            "constraint_summary": {
                "total_constraints_applied": len(applied_constraints),
                "causes_eliminated": len(verified_causes) - len(feasible_interventions),
                "feasible_count": len(feasible_interventions),
            },
            "business_context": input_context.get("business_context", ""),
        }

        return {
            "constrained_brief": constrained_brief,
            "current_node": "constraint_add",
        }

    except Exception as e:
        return {
            "constrained_brief": {
                "verified_causes": state.get("verified_root_causes", []),
                "applied_constraints": [],
                "feasible_interventions": [],
                "priority_ranking": [],
            },
            "errors": [*state.get("errors", []), f"Constraint add error: {str(e)}"],
            "current_node": "constraint_add",
        }
