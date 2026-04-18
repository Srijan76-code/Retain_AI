"""
Node 7: Constraint Add
========================
Action:  Reality filtering
Tools:   Hard-coded logic
Adds:    constrained_brief
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def constraint_add_node(state: RetentionGraphState) -> dict:
    """
    Apply real-world constraints to the verified root causes.

    TODO: Replace dummy logic with actual implementation:
      - Filter root causes against business constraints (budget, timeline, legal)
      - Remove infeasible interventions
      - Rank remaining causes by actionability
      - Produce a constrained brief for strategy generation
    """
    # ── Dummy implementation — replace with actual code ──────────────
    constrained_brief = {
        "verified_causes": state.get("verified_root_causes", []),
        "applied_constraints": [],
        "feasible_interventions": [],
        "priority_ranking": [],
    }

    return {
        "constrained_brief": constrained_brief,
        "current_node": "constraint_add",
    }
