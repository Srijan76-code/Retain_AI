"""
Node 9d: Strategy Merge
=========================
Merges outputs from the three parallel Execution Agents
into unified strategy_outputs.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def strategy_merge_node(state: RetentionGraphState) -> dict:
    """Merge outputs from three Execution Agents into ranked recommendations."""
    try:
        economist_output = state.get("unit_economist_output", {})
        jtbd_output = state.get("jtbd_specialist_output", {})
        growth_output = state.get("growth_hacker_output", {})

        merged_strategies = _merge_strategy_outputs(economist_output, jtbd_output, growth_output)

        strategy_outputs = {
            "unit_economics_strategy": economist_output,
            "jtbd_strategy": jtbd_output,
            "growth_strategy": growth_output,
            "merged_strategies": merged_strategies,
            "strategy_summary": {
                "total_recommendations": len(merged_strategies),
                "frameworks_applied": [
                    f for f in [
                        "Unit Economics" if not economist_output.get("error") else None,
                        "Jobs-to-be-Done" if not jtbd_output.get("error") else None,
                        "Growth Hacking" if not growth_output.get("error") else None,
                    ] if f
                ],
                "consensus_recommendation": merged_strategies[0] if merged_strategies else {},
            },
        }

        iteration_count = state.get("iteration_count", 0) + 1

        return {
            "strategy_outputs": strategy_outputs,
            "iteration_count": iteration_count,
            "current_node": "strategy_merge",
        }

    except Exception as e:
        return {
            "strategy_outputs": {"merged_strategies": [], "error": str(e)},
            "iteration_count": state.get("iteration_count", 0) + 1,
            "errors": [f"Strategy merge error: {str(e)}"],
            "current_node": "strategy_merge",
        }


def _merge_strategy_outputs(economist: dict, jtbd: dict, growth: dict) -> list[dict]:
    """Merge outputs from three agents into ranked recommendations using real agent data."""
    merged = []
    rank = 1

    # Unit Economist — pull real data from agent output
    if not economist.get("error"):
        top = economist.get("top_roi_intervention", {})
        interventions = economist.get("proposed_interventions", [])
        if top or interventions:
            best = top if top else interventions[0]
            merged.append({
                "rank": rank,
                "recommendation": best.get("intervention", ""),
                "framework": economist.get("framework", "Unit Economics"),
                "expected_roi": best.get("expected_roi", 0),
                "confidence": best.get("confidence", economist.get("confidence", 0)),
                "rationale": best.get("rationale", ""),
                "estimated_cost": best.get("estimated_cost", ""),
                "cost_usd": best.get("cost_usd", 0),
            })
            rank += 1

    # JTBD Specialist — pull real data from agent output
    if not jtbd.get("error"):
        interventions = jtbd.get("proposed_interventions", [])
        if interventions:
            best = interventions[0]
            merged.append({
                "rank": rank,
                "recommendation": best.get("intervention", ""),
                "framework": jtbd.get("framework", "Jobs-to-be-Done"),
                "expected_impact": best.get("expected_impact", 0),
                "confidence": best.get("confidence", jtbd.get("confidence", 0)),
                "rationale": best.get("rationale", ""),
                "job_focus": best.get("job_focus", ""),
                "implementation_effort": best.get("implementation_effort", ""),
            })
            rank += 1

    # Growth Hacker — pull real data from agent output
    if not growth.get("error"):
        tactics = growth.get("proposed_tactics", [])
        if tactics:
            best = tactics[0]
            merged.append({
                "rank": rank,
                "recommendation": best.get("name", ""),
                "framework": growth.get("framework", "Growth Hacking"),
                "expected_lift": best.get("expected_lift", 0),
                "confidence": best.get("confidence", growth.get("confidence", 0)),
                "rationale": best.get("description", ""),
                "target_metric": best.get("target_metric", ""),
                "implementation_timeline": best.get("implementation_timeline", ""),
            })
            rank += 1

    return merged
