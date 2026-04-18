"""
Node 11: Strategy Critic
==========================
Action:  Senior partner review with iteration control
Tools:   LLM (senior partner persona)
Adds:    critic_verdict, iteration_count

Conditional routing after this node:
  - Approved              → Node 12 (Execution Architect)
  - Low Lift / Violation   → Node 9  (Strategy Pod — re-run Execution Agents)
  - Failure after 3+ iters → Node 5  (Diagnosis Pod — back to Discovery Agents)
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def strategy_critic_node(state: RetentionGraphState) -> dict:
    """
    Senior-partner-level review of the proposed strategy + simulations.

    TODO: Replace dummy logic with actual implementation:
      - Evaluate strategy quality, feasibility, and expected lift
      - Check for constraint violations
      - If lift too low or constraints violated, reject
      - Track iteration count for the loop-back limit
      - Use LLM with "senior partner" persona for critique
    """
    # ── Dummy implementation — replace with actual code ──────────────
    current_iterations = state.get("iteration_count", 0) + 1
    critic_verdict = "approved"  # placeholder: "approved" | "low_lift" | "violation"

    return {
        "critic_verdict": critic_verdict,
        "iteration_count": current_iterations,
        "current_node": "strategy_critic",
    }
