"""
Node 12: Execution Architect
===============================
Action:  Generate 30/60/90-day roadmap
Tools:   Template generation
Adds:    final_playbook
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from datetime import datetime, timedelta


def execution_architect_node(state: RetentionGraphState) -> dict:
    """Produce the final execution playbook with 30/60/90-day roadmap."""
    try:
        merged_strategies = state.get("strategy_outputs", {}).get("merged_strategies", [])
        lift_percent = state.get("lift_percent", 15.0)
        input_context = state.get("input_context", {})

        # Generate 30/60/90 day roadmap
        roadmap = generate_roadmap(merged_strategies, lift_percent)

        # Create final playbook
        final_playbook = {
            "title": "Retention Optimization Playbook",
            "created_date": datetime.now().isoformat(),
            "company": input_context.get("industry", "SaaS"),
            "size": input_context.get("company_size", "Unknown"),
            "estimated_total_lift": round(lift_percent, 1),
            "confidence_level": "High" if lift_percent > 15 else "Medium",

            "executive_summary": {
                "objective": f"Improve retention by {round(lift_percent, 1)}% over 90 days",
                "key_strategies": [s.get("recommendation", "") for s in merged_strategies[:3]],
                "expected_impact": f"${round(lift_percent * 10000, 0):,.0f} incremental ARR",
                "resource_requirement": determine_resource_requirement(merged_strategies),
            },

            "30_day_plan": {
                "phase": "Foundation & Quick Wins",
                "initiatives": roadmap["30_day"],
                "kpis": [
                    {"metric": "Day-7 activation rate", "target": "+5%", "owner": "Product"},
                    {"metric": "Support ticket resolution time", "target": "-20%", "owner": "CS"},
                ],
                "success_criteria": "Achieve >50% of 30-day initiatives",
                "risk_mitigation": "Weekly progress reviews; escalate blockers by Wednesday",
            },

            "60_day_plan": {
                "phase": "Momentum & Scale",
                "initiatives": roadmap["60_day"],
                "kpis": [
                    {"metric": "Month-2 cohort retention", "target": "+8%", "owner": "Product"},
                    {"metric": "Feature adoption rate", "target": "+15%", "owner": "Product"},
                ],
                "success_criteria": "30-day initiatives delivering projected lift",
                "risk_mitigation": "Expand team; set up automated reporting",
            },

            "90_day_plan": {
                "phase": "Optimization & Refinement",
                "initiatives": roadmap["90_day"],
                "kpis": [
                    {"metric": "3-month retention lift", "target": f"+{round(lift_percent * 0.7, 1)}%", "owner": "Analytics"},
                    {"metric": "Net Retention", "target": "+10%", "owner": "Executive"},
                ],
                "success_criteria": f"Achieve {round(lift_percent * 0.8, 1)}% of projected lift",
                "risk_mitigation": "Prepare follow-on initiatives for Q2",
            },

            "team_structure": {
                "executive_sponsor": "VP Product / Chief Revenue Officer",
                "product_lead": "Product Manager (Retention)",
                "data_analyst": "Analytics Engineer",
                "contributors": ["Customer Success", "Engineering", "Marketing"],
            },

            "budget_estimate": {
                "technology": "$15,000",
                "people": "$50,000 (2 FTE for 3 months)",
                "marketing": "$10,000",
                "total": "$75,000",
            },

            "success_metrics": {
                "primary": f"Achieve >{round(lift_percent * 0.8, 1)}% retention improvement",
                "secondary": [
                    "Improve Day-7 activation by >5%",
                    "Increase feature adoption by >15%",
                    "Reduce support resolution time by >15%",
                ],
                "measurement_frequency": "Weekly dashboards; monthly business reviews",
            },

            "contingency": {
                "if_behind_pace": "Increase A/B test intensity; escalate to executive steering",
                "if_exceeding_goals": "Expand scope; pursue additional retention initiatives",
                "review_cadence": "Weekly ops review; bi-weekly steering committee",
            },
        }

        return {
            "final_playbook": final_playbook,
            "playbook_status": "approved_for_execution",
            "current_node": "execution_architect",
        }

    except Exception as e:
        return {
            "final_playbook": {
                "title": "Retention Optimization Playbook (Draft)",
                "status": "error",
                "error": str(e),
            },
            "errors": [*state.get("errors", []), f"Execution architect error: {str(e)}"],
            "current_node": "execution_architect",
        }


def generate_roadmap(strategies: list, lift_percent: float) -> dict:
    """Generate phased 30/60/90 roadmap based on strategies."""
    roadmap = {
        "30_day": [],
        "60_day": [],
        "90_day": [],
    }

    # Distribute strategies across phases
    for i, strategy in enumerate(strategies[:3]):
        initiative = {
            "name": strategy.get("recommendation", f"Initiative {i+1}"),
            "description": f"Execute {strategy.get('framework', 'strategy')} recommendation",
            "owner": "TBD",
            "effort": "medium",
            "expected_lift": round(lift_percent / 3, 1),
        }

        if i == 0:
            roadmap["30_day"].append({**initiative, "timeline": "Weeks 1-2", "status": "planning"})
        elif i == 1:
            roadmap["60_day"].append({**initiative, "timeline": "Weeks 3-5", "status": "planning"})
        else:
            roadmap["90_day"].append({**initiative, "timeline": "Weeks 6-9", "status": "planning"})

    # Add standard initiatives
    roadmap["30_day"].extend([
        {
            "name": "Deploy analytics instrumentation",
            "description": "Set up detailed tracking for retention KPIs",
            "owner": "Analytics",
            "effort": "low",
            "timeline": "Week 1",
        },
        {
            "name": "Kickoff discovery with customer interviews",
            "description": "Validate hypotheses with 10+ interviews",
            "owner": "Product",
            "effort": "medium",
            "timeline": "Weeks 1-2",
        },
    ])

    roadmap["60_day"].extend([
        {
            "name": "Launch A/B tests for top 2 initiatives",
            "description": "Run simultaneous tests; measure impact",
            "owner": "Analytics",
            "effort": "high",
            "timeline": "Weeks 3-4",
        },
    ])

    roadmap["90_day"].extend([
        {
            "name": "Full rollout of winning strategies",
            "description": "Scale validated tactics to 100% of user base",
            "owner": "Product",
            "effort": "high",
            "timeline": "Weeks 8-9",
        },
    ])

    return roadmap


def determine_resource_requirement(strategies: list) -> str:
    """Determine resource needs based on strategy complexity."""
    if len(strategies) >= 3:
        return "3-4 FTE (Product, Analytics, Engineering, CS Lead)"
    elif len(strategies) >= 2:
        return "2-3 FTE (Product, Analytics, CS)"
    else:
        return "1-2 FTE (Product, Analytics)"
