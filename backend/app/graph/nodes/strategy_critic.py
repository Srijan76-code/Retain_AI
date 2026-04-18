"""
Node 11: Strategy Critic
==========================
Action:  Senior partner review with iteration control
Tools:   LLM (senior partner persona)
Adds:    critic_verdict, iteration_count
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json


def strategy_critic_node(state: RetentionGraphState) -> dict:
    """Senior-partner-level review of the proposed strategy."""
    try:
        merged_strategies = state.get("strategy_outputs", {}).get("merged_strategies", [])
        lift_percent = state.get("lift_percent", 0)
        iteration_count = state.get("iteration_count", 0) + 1
        constrained_brief = state.get("constrained_brief", {})
        human_feedback = state.get("human_clarification", {}).get("responses", {})

        # Evaluate strategy quality
        evaluation = evaluate_strategy(merged_strategies, lift_percent, human_feedback)

        # Determine verdict
        if evaluation["quality_score"] >= 0.75 and lift_percent >= 12:
            critic_verdict = "approved"
            feedback = "Strategy meets quality and impact thresholds. Proceed to execution planning."
        elif evaluation["constraint_violations"] > 0:
            critic_verdict = "violation"
            feedback = f"Strategy violates {evaluation['constraint_violations']} constraint(s). Iterate on discovery."
        elif lift_percent < 12:
            critic_verdict = "low_lift"
            feedback = f"Expected lift of {lift_percent}% below 12% threshold. Re-run execution agents with adjusted parameters."
        else:
            critic_verdict = "low_lift"
            feedback = "Strategy quality insufficient. Additional refinement needed."

        criticism = {
            "quality_score": round(evaluation["quality_score"], 3),
            "lift_assessment": f"{lift_percent}% projected lift",
            "constraint_violations": evaluation["constraint_violations"],
            "critical_feedback": evaluation.get("critical_feedback", []),
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", []),
            "recommendations": evaluation.get("recommendations", []),
        }

        return {
            "critic_verdict": critic_verdict,
            "iteration_count": iteration_count,
            "criticism": criticism,
            "feedback": feedback,
            "current_node": "strategy_critic",
        }

    except Exception as e:
        return {
            "critic_verdict": "low_lift",
            "iteration_count": state.get("iteration_count", 0) + 1,
            "criticism": {"error": str(e)},
            "feedback": "Critique error; defaulting to re-iteration",
            "errors": [*state.get("errors", []), f"Strategy critic error: {str(e)}"],
            "current_node": "strategy_critic",
        }


def evaluate_strategy(strategies: list, lift_percent: float, human_feedback: dict) -> dict:
    """Evaluate strategy quality, feasibility, and constraint satisfaction."""
    evaluation = {
        "quality_score": 0.0,
        "constraint_violations": 0,
        "strengths": [],
        "weaknesses": [],
        "critical_feedback": [],
        "recommendations": [],
    }

    # Base quality from number of recommendations
    base_quality = min(len(strategies) / 3.0, 1.0)

    # Lift quality adjustment
    lift_quality = min(lift_percent / 25, 1.0)  # 25% = 1.0

    # Check for constraint violations
    violations = 0
    if lift_percent < 8:
        violations += 1
        evaluation["weaknesses"].append("Low projected lift (<8%)")
    if len(strategies) < 1:
        violations += 1
        evaluation["weaknesses"].append("Insufficient strategy options")

    evaluation["constraint_violations"] = violations

    # Calculate composite quality score
    quality = (base_quality * 0.4) + (lift_quality * 0.6)
    evaluation["quality_score"] = max(0, min(quality, 1.0))

    # Add feedback
    if len(strategies) > 0:
        evaluation["strengths"].append(f"{len(strategies)} well-researched intervention options")
    if lift_percent >= 15:
        evaluation["strengths"].append(f"Strong projected impact ({lift_percent}%)")
    if lift_percent < 12:
        evaluation["weaknesses"].append(f"Conservative impact estimate ({lift_percent}%)")

    # Recommendations
    if len(strategies) == 0:
        evaluation["recommendations"].append("Return to discovery phase for additional hypothesis generation")
    if lift_percent < 12:
        evaluation["recommendations"].append("Consider increasing scope or combining multiple tactics")
    if quality > 0.75:
        evaluation["recommendations"].append("Prioritize quick-win tactics for immediate momentum")

    return evaluation
