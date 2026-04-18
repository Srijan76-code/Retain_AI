"""
Graph State — Shared state flowing through every node.
========================================================
Each node reads from and writes to this TypedDict.
Add new keys as nodes produce artefacts.
"""

from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict


class RetentionGraphState(TypedDict, total=False):
    """
    Cumulative state passed between LangGraph nodes.

    Keys are added progressively as described in the Excalidraw diagram:
      Node 1  → input_context, input_constraints
      Node 2  → data_quality_score, data_quality_logs
      Node 3  → feature_store
      Node 4  → behavior_curves, behavior_cohorts
      Node 5  → diagnosis_results (from parallel Discovery Agents)
      Node 6  → hypothesis_status, verified_root_causes
      Node 7  → constrained_brief
      Node 8  → human_clarification
      Node 9  → strategy_outputs (from parallel Execution Agents)
      Node 10 → simulations, lift_percent
      Node 11 → critic_verdict, iteration_count
      Node 12 → final_playbook
    """

    # ── Input ────────────────────────────────────────────────────────
    raw_csv_path: str
    questionnaire: dict[str, Any]

    # ── Node 1: Input Ingest ─────────────────────────────────────────
    input_context: dict[str, Any]
    input_constraints: dict[str, Any]

    # ── Node 2: Data Audit ───────────────────────────────────────────
    data_quality_score: float
    data_quality_logs: list[str]

    # ── Node 3: Feature Engineering ──────────────────────────────────
    feature_store: dict[str, Any]

    # ── Node 4: Behavioral Map ───────────────────────────────────────
    behavior_curves: dict[str, Any]
    behavior_cohorts: list[dict[str, Any]]

    # ── Node 5: Diagnosis Pod (parallel Discovery Agents) ────────────
    forensic_detective_output: dict[str, Any]
    pattern_matcher_output: dict[str, Any]
    professional_skeptic_output: dict[str, Any]
    diagnosis_results: dict[str, Any]

    # ── Node 6: Hypothesis Validation ────────────────────────────────
    hypothesis_status: str  # "verified" | "weak_proof" | "unverified"
    verified_root_causes: list[dict[str, Any]]

    # ── Node 7: Constraint Add ───────────────────────────────────────
    constrained_brief: dict[str, Any]

    # ── Node 8: Adaptive HITL ────────────────────────────────────────
    human_clarification: dict[str, Any]
    hitl_questions: list[str]

    # ── Node 9: Strategy Pod (parallel Execution Agents) ─────────────
    unit_economist_output: dict[str, Any]
    jtbd_specialist_output: dict[str, Any]
    growth_hacker_output: dict[str, Any]
    strategy_outputs: dict[str, Any]

    # ── Node 10: Simulation ──────────────────────────────────────────
    simulations: dict[str, Any]
    lift_percent: float

    # ── Node 11: Strategy Critic ─────────────────────────────────────
    critic_verdict: str  # "approved" | "low_lift" | "violation"
    iteration_count: int

    # ── Node 12: Execution Architect ─────────────────────────────────
    final_playbook: dict[str, Any]

    # ── Metadata / Control ───────────────────────────────────────────
    errors: list[str]
    current_node: str
    retry_count: int
    discovery_attempts: int
