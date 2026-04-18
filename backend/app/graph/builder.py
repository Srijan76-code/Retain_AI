"""
Graph Builder — Wires all 12 nodes + conditional edges into a LangGraph.
=========================================================================
This is the single source of truth for the pipeline topology.
Matches the Excalidraw diagram exactly.

Flow:
  Input → Node 1 → Node 2 ─┬─ Clean ──→ Node 3 → Node 4 → Node 5 (Diagnosis Pod)
                             │                                  ↓
                             └─ Score < T → Retry → Node 1     Node 5 spawns:
                                                                 • Forensic Detective
                                                                 • Pattern Matcher
                                                                 • Professional Skeptic
                                                                  ↓
                                                          Node 6 (Hypo. Validate)
                                                           ├─ Verified → Node 7 → Node 8 → Node 9 (Strategy Pod)
                                                           └─ Weak     → Node 5 (loop back)
                                                                                      ↓
                                                                               Node 9 spawns:
                                                                                 • Unit Economist
                                                                                 • JTBD Specialist
                                                                                 • Growth Hacker
                                                                                  ↓
                                                                            Node 10 → Node 11 (Critic)
                                                                                       ├─ Approved    → Node 12 → END
                                                                                       ├─ Low Lift    → Node 9 (loop back)
                                                                                       └─ Fail 3+     → Node 5 (loop back)
"""

from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import RetentionGraphState
from app.graph.conditions import (
    route_after_data_audit,
    route_after_retry,
    route_after_hypothesis_validation,
    route_after_strategy_critic,
)
from app.graph.nodes import (
    input_ingest_node,
    data_audit_node,
    feature_engineering_node,
    behavioral_map_node,
    diagnosis_pod_node,
    hypothesis_validation_node,
    constraint_add_node,
    adaptive_hitl_node,
    strategy_pod_node,
    simulation_node,
    strategy_critic_node,
    execution_architect_node,
    retry_handler_node,
)


def build_retention_graph() -> StateGraph:
    """
    Construct and compile the full 12-node retention analysis graph.

    Returns a compiled LangGraph ready to `.invoke()` or `.stream()`.
    """
    graph = StateGraph(RetentionGraphState)

    # ── Register all nodes ───────────────────────────────────────────
    graph.add_node("input_ingest", input_ingest_node)
    graph.add_node("data_audit", data_audit_node)
    graph.add_node("retry_handler", retry_handler_node)
    graph.add_node("feature_engineering", feature_engineering_node)
    graph.add_node("behavioral_map", behavioral_map_node)
    graph.add_node("diagnosis_pod", diagnosis_pod_node)
    graph.add_node("hypothesis_validation", hypothesis_validation_node)
    graph.add_node("constraint_add", constraint_add_node)
    graph.add_node("adaptive_hitl", adaptive_hitl_node)
    graph.add_node("strategy_pod", strategy_pod_node)
    graph.add_node("simulation", simulation_node)
    graph.add_node("strategy_critic", strategy_critic_node)
    graph.add_node("execution_architect", execution_architect_node)

    # ── Entry point ──────────────────────────────────────────────────
    graph.set_entry_point("input_ingest")

    # ── Linear edges ─────────────────────────────────────────────────
    graph.add_edge("input_ingest", "data_audit")

    # Node 2 → conditional: clean vs retry
    graph.add_conditional_edges(
        "data_audit",
        route_after_data_audit,
        {
            "feature_engineering": "feature_engineering",
            "retry_handler": "retry_handler",
        },
    )

    # Retry loops back to input ingest, or ends if max retries exceeded
    graph.add_conditional_edges(
        "retry_handler",
        route_after_retry,
        {
            "input_ingest": "input_ingest",
            END: END,
        },
    )

    # Node 3 → Node 4 → Node 5
    graph.add_edge("feature_engineering", "behavioral_map")
    graph.add_edge("behavioral_map", "diagnosis_pod")

    # Node 5 → Node 6
    graph.add_edge("diagnosis_pod", "hypothesis_validation")

    # Node 6 → conditional: verified vs weak proof
    graph.add_conditional_edges(
        "hypothesis_validation",
        route_after_hypothesis_validation,
        {
            "constraint_add": "constraint_add",
            "diagnosis_pod": "diagnosis_pod",  # loop back to discovery
            END: END,                           # give up after max attempts
        },
    )

    # Node 7 → Node 8 → Node 9
    graph.add_edge("constraint_add", "adaptive_hitl")
    graph.add_edge("adaptive_hitl", "strategy_pod")

    # Node 9 → Node 10 → Node 11
    graph.add_edge("strategy_pod", "simulation")
    graph.add_edge("simulation", "strategy_critic")

    # Node 11 → conditional: approved vs low-lift vs failure
    graph.add_conditional_edges(
        "strategy_critic",
        route_after_strategy_critic,
        {
            "execution_architect": "execution_architect",
            "strategy_pod": "strategy_pod",    # low lift → re-run execution agents
            "diagnosis_pod": "diagnosis_pod",  # 3+ failures → back to discovery
        },
    )

    # Node 12 → END
    graph.add_edge("execution_architect", END)

    # ── Compile with Memory for HITL ─────────────────────────────────
    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["adaptive_hitl"])
