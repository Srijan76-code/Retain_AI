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
DATA_QUALITY_THRESHOLD = 0.5  # Lowered to reduce unnecessary retries
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


# ── After Hypothesis Validation ──────────────────────────────────────
MAX_DISCOVERY_ATTEMPTS = 3


def route_after_hypothesis_validation(
    state: RetentionGraphState,
) -> Literal["constraint_add", "diagnosis_pod", "__end__"]:
    """
    Verified root cause       → proceed to Constraint Add.
    Unverified / Weak Proof   → loop back to Discovery (fan-out).
    Attempts >= max           → end graph.
    """
    if state.get("hypothesis_status") == "verified":
        return "constraint_add"
    if state.get("discovery_attempts", 0) >= MAX_DISCOVERY_ATTEMPTS:
        return END
    return "diagnosis_pod"


# ── After Strategy Critic ────────────────────────────────────────────
MAX_CRITIC_ITERATIONS = 3


def route_after_strategy_critic(
    state: RetentionGraphState,
) -> Literal["execution_architect", "strategy_pod", "diagnosis_pod"]:
    """
    Approved                → proceed to Execution Architect.
    Low Lift / Violation    → loop back to Execution Agents (fan-out).
    Failure after 3+ iters  → loop back to Discovery (fan-out).
    """
    verdict = state.get("critic_verdict", "")
    iterations = state.get("iteration_count", 0)

    if verdict == "approved":
        return "execution_architect"

    if iterations >= MAX_CRITIC_ITERATIONS:
        return "diagnosis_pod"

    return "strategy_pod"
