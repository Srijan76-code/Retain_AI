"""
Edge Conditions — Routing logic between nodes.
================================================
Each function returns the name of the next node (or END).
Used as `conditional_edge` callbacks in the graph builder.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END

from app.graph.state import RetentionGraphState


# ── After Node 2: Data Audit ─────────────────────────────────────────
DATA_QUALITY_THRESHOLD = 0.7  # TODO: make configurable
MAX_RETRIES = 3


def route_after_data_audit(
    state: RetentionGraphState,
) -> Literal["feature_engineering", "retry_handler"]:
    """
    If data quality score >= threshold → proceed to Feature Engineering.
    Otherwise → route to Retry Handler (request better data).
    """
    score = state.get("data_quality_score", 0.0)
    if score >= DATA_QUALITY_THRESHOLD:
        return "feature_engineering"
    return "retry_handler"


# ── After Retry Handler ──────────────────────────────────────────────
def route_after_retry(
    state: RetentionGraphState,
) -> Literal["input_ingest", "__end__"]:
    """
    If retry attempts exceeded → end the graph (give up).
    Otherwise → loop back to input_ingest for fresh data.
    """
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return END
    return "input_ingest"


# ── After Node 6: Hypothesis Validation ──────────────────────────────
MAX_DISCOVERY_ATTEMPTS = 3


def route_after_hypothesis_validation(
    state: RetentionGraphState,
) -> Literal["constraint_add", "diagnosis_pod", "__end__"]:
    """
    Verified root cause       → proceed to Constraint Add (Node 7).
    Unverified / Weak Proof   → loop back to Diagnosis Pod (Node 5).
    Attempts >= max           → end graph (give up on discovery).
    """
    if state.get("discovery_attempts", 0) >= MAX_DISCOVERY_ATTEMPTS:
        return END
    if state.get("hypothesis_status") == "verified":
        return "constraint_add"
    return "diagnosis_pod"


# ── After Node 11: Strategy Critic ───────────────────────────────────
MAX_CRITIC_ITERATIONS = 3


def route_after_strategy_critic(
    state: RetentionGraphState,
) -> Literal["execution_architect", "strategy_pod", "diagnosis_pod"]:
    """
    Approved                → proceed to Execution Architect (Node 12).
    Low Lift / Violation    → loop back to Strategy Pod (Node 9)
                              which re-runs Execution Agents.
    Failure after 3+ iters  → loop all the way back to Diagnosis Pod (Node 5)
                              to re-discover from scratch.
    """
    verdict = state.get("critic_verdict", "")
    iterations = state.get("iteration_count", 0)

    if verdict == "approved":
        return "execution_architect"

    if iterations >= MAX_CRITIC_ITERATIONS:
        # Failure Iter 3+ → back to Discovery Agents
        return "diagnosis_pod"

    # Low Lift / Violation → back to Execution Agents
    return "strategy_pod"
