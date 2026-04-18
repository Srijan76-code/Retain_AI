"""
Execution Agent: Growth Hacker
================================
Applies growth frameworks and tactics.
Called by: strategy_pod_node
"""

from __future__ import annotations

from typing import Any
from app.graph.state import RetentionGraphState


def run_growth_hacker(state: RetentionGraphState) -> dict[str, Any]:
    """Generate growth-focused retention strategies."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        constrained_brief = state.get("constrained_brief", {})
        feasible_interventions = constrained_brief.get("feasible_interventions", [])

        proposed_tactics = []
        experiment_designs = []
        activation_improvements = []
        viral_loops = []

        # 1. Design activation improvement tactics
        if feasible_interventions:
            for intervention in feasible_interventions[:2]:
                cause = intervention.get("cause", "")
                confidence = intervention.get("confidence", 0)

                # Activation tactic
                tactic = {
                    "name": f"Activation boost: {cause}",
                    "description": f"Improve {cause.lower()} within first 30 days",
                    "target_metric": "Day-30 activation rate",
                    "expected_lift": round(confidence * 20, 1),
                    "implementation_timeline": "2-3 weeks",
                }
                proposed_tactics.append(tactic)

                # A/B test design
                experiment = {
                    "test_name": f"Test_{cause.replace(' ', '_')}",
                    "control": "Current experience",
                    "variant": f"Enhanced {cause.lower()}",
                    "metric": "7-day retention",
                    "sample_size": 1000,
                    "duration_days": 14,
                }
                experiment_designs.append(experiment)

                # Activation improvement
                improvement = {
                    "focus": "Onboarding",
                    "current_step": f"Baseline {cause}",
                    "improvement": f"Guided {cause.lower()} workflow",
                    "estimated_lift": round(confidence * 15, 1),
                }
                activation_improvements.append(improvement)

        # 2. Identify viral/retention loops
        viral_loops = [
            {
                "loop": "Engagement loop: Use → Invite → Collaborator → Retention",
                "trigger": "First collaboration milestone",
                "incentive": "Unlock advanced features",
                "estimated_impact": "5-10% retention lift",
            },
            {
                "loop": "Value reinforcement: Achieve goal → See results → Renew subscription",
                "trigger": "Goal completion",
                "incentive": "Exclusive insights",
                "estimated_impact": "8-12% retention lift",
            },
        ]

        # 3. Speed-to-impact ranking
        speed_to_impact = {
            "quick_wins": proposed_tactics[:1],
            "medium_term": proposed_tactics[1:2],
            "long_term": [],
            "prioritization_logic": "Combination of implementation speed and expected impact",
        }

        return {
            "agent": "growth_hacker",
            "proposed_tactics": proposed_tactics,
            "experiment_designs": experiment_designs,
            "viral_loops": viral_loops,
            "activation_improvements": activation_improvements,
            "speed_to_impact": speed_to_impact,
            "framework": "Pirate Metrics (AARRR)",
            "confidence": 0.70,
        }

    except Exception as e:
        return {
            "agent": "growth_hacker",
            "proposed_tactics": [],
            "experiment_designs": [],
            "viral_loops": [],
            "activation_improvements": [],
            "speed_to_impact": {},
            "error": str(e),
        }
