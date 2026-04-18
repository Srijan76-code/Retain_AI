"""
Node 8: Adaptive HITL (Human-in-the-Loop)
==========================================
Action:  Ask 1–3 targeted clarification questions
Tools:   LLM Chat Agent
Adds:    human_clarification, hitl_questions
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def adaptive_hitl_node(state: RetentionGraphState) -> dict:
    """
    Generate targeted questions and incorporate human responses.

    TODO: Replace dummy logic with actual implementation:
      - Analyse constrained_brief to identify information gaps
      - Generate 1–3 smart, targeted questions via LLM
      - Present questions to user (via API / websocket)
      - Incorporate human answers into the state
    """
    # ── Dummy implementation — replace with actual code ──────────────
    hitl_questions = [
        "Placeholder question 1: What is your primary retention KPI?",
        "Placeholder question 2: What interventions have you tried before?",
    ]
    human_clarification = {
        "questions_asked": hitl_questions,
        "responses": {},  # Will be filled after human responds
    }

    return {
        "hitl_questions": hitl_questions,
        "human_clarification": human_clarification,
        "current_node": "adaptive_hitl",
    }
