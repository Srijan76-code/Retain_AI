"""
Node 9: Strategy Pod
=====================
Action:  Parallel synthesis via Execution Agents
Tools:   JTBD Frameworks, Growth Frameworks
Spawns:  Unit Economist, JTBD Specialist, Growth Hacker

This node orchestrates three execution agents in parallel
and merges their strategy outputs.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from app.graph.agents.execution.unit_economist import run_unit_economist
from app.graph.agents.execution.jtbd_specialist import run_jtbd_specialist
from app.graph.agents.execution.growth_hacker import run_growth_hacker


def strategy_pod_node(state: RetentionGraphState) -> dict:
    """
    Run three Execution Agents in parallel, then merge strategies.

    TODO: Replace dummy logic with actual implementation:
      - Fan-out to Unit Economist, JTBD Specialist, Growth Hacker
      - Each agent generates strategies from their framework's perspective
      - Merge / reconcile into unified strategy_outputs
    """
    # ── Run Execution Agents (sequentially for now; parallelise later) ──
    economist_output = run_unit_economist(state)
    jtbd_output = run_jtbd_specialist(state)
    growth_output = run_growth_hacker(state)

    # ── Merge results ────────────────────────────────────────────────
    strategy_outputs = {
        "unit_economics_strategy": economist_output,
        "jtbd_strategy": jtbd_output,
        "growth_strategy": growth_output,
        "merged_strategies": [],  # TODO: implement merge logic
    }

    return {
        "unit_economist_output": economist_output,
        "jtbd_specialist_output": jtbd_output,
        "growth_hacker_output": growth_output,
        "strategy_outputs": strategy_outputs,
        "current_node": "strategy_pod",
    }
