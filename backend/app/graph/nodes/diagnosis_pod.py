"""
Node 5: Diagnosis Pod
======================
Action:  Parallel analysis via Discovery Agents
Tools:   SHAP, BERTopic
Spawns:  Forensic Detective, Pattern Matcher, Professional Skeptic

This node orchestrates three discovery agents in parallel
and merges their outputs into a unified diagnosis.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from app.graph.agents.discovery.forensic_detective import run_forensic_detective
from app.graph.agents.discovery.pattern_matcher import run_pattern_matcher
from app.graph.agents.discovery.professional_skeptic import run_professional_skeptic


def diagnosis_pod_node(state: RetentionGraphState) -> dict:
    """
    Run three Discovery Agents in parallel, then merge findings.

    TODO: Replace dummy logic with actual implementation:
      - Fan-out to Forensic Detective, Pattern Matcher, Professional Skeptic
      - Each agent analyses features + behavioral data from different angles
      - Merge / reconcile outputs into unified diagnosis_results
    """
    # ── Run Discovery Agents (sequentially for now; parallelise later) ──
    forensic_output = run_forensic_detective(state)
    pattern_output = run_pattern_matcher(state)
    skeptic_output = run_professional_skeptic(state, forensic_output, pattern_output)

    # ── Merge results ────────────────────────────────────────────────
    diagnosis_results = {
        "forensic_findings": forensic_output,
        "pattern_findings": pattern_output,
        "skeptic_findings": skeptic_output,
        "merged_hypotheses": [],  # TODO: implement merge logic
    }

    return {
        "forensic_detective_output": forensic_output,
        "pattern_matcher_output": pattern_output,
        "professional_skeptic_output": skeptic_output,
        "diagnosis_results": diagnosis_results,
        "current_node": "diagnosis_pod",
    }
