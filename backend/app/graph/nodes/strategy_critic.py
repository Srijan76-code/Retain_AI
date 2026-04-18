"""
Node 11: Strategy Critic
==========================
Action:  Senior partner review with iteration control
Tools:   Groq LLM (senior partner persona)
Adds:    critic_verdict, iteration_count, criticism, feedback
"""

from __future__ import annotations

import os
import json
from pydantic import BaseModel, Field
from typing import List, Literal

from app.graph.state import RetentionGraphState
from app.graph.utils import safe_llm_invoke
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class CriticEvaluation(BaseModel):
    quality_score: float = Field(description="Score from 0.0 to 1.0 reflecting strategy quality")
    strengths: List[str]
    weaknesses: List[str]
    critical_feedback: List[str]
    recommendations: List[str]
    constraint_violations: int
    verdict: Literal["approved", "low_lift", "violation"]
    verdict_reason: str


def strategy_critic_node(state: RetentionGraphState) -> dict:
    """Senior-partner-level review of the proposed strategy using LLM."""
    try:
        merged_strategies = state.get("strategy_outputs", {}).get("merged_strategies", [])
        lift_percent = state.get("lift_percent", 0)
        iteration_count = state.get("iteration_count", 0) + 1
        constrained_brief = state.get("constrained_brief", {})
        human_feedback = state.get("human_clarification", {}).get("responses", {})
        verified_causes = state.get("verified_root_causes", [])

        # Use Groq LLM for real evaluation
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_2"),
            temperature=0.1,
        )

        prompt = ChatPromptTemplate.from_template(
            """You are a senior strategy partner reviewing a retention strategy proposal.

## Proposed Strategies
{strategies}

## Verified Root Causes
{causes}

## Simulation Results
Projected Lift: {lift}%

## Constraints
{constraints}

## Human Feedback
{feedback}

Evaluate this strategy critically. Consider:
1. Does the strategy address the actual root causes?
2. Is the projected lift realistic?
3. Are there any constraint violations?
4. What are the strengths and weaknesses?

Return ONLY a valid JSON object:
{{
    "quality_score": 0.75,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1"],
    "critical_feedback": ["feedback 1"],
    "recommendations": ["recommendation 1"],
    "constraint_violations": 0,
    "verdict": "approved|low_lift|violation",
    "verdict_reason": "Why this verdict was chosen"
}}"""
        )

        evaluation = safe_llm_invoke(
            llm, CriticEvaluation,
            prompt.format(
                strategies=json.dumps(merged_strategies, indent=2)[:2000],
                causes=json.dumps(verified_causes, indent=2)[:1000],
                lift=lift_percent,
                constraints=json.dumps(constrained_brief, indent=2)[:1000],
                feedback=json.dumps(human_feedback)[:500] if human_feedback else "No human feedback",
            ),
            agent_name="StrategyCritic",
        )

        quality_score = evaluation.quality_score
        llm_verdict = evaluation.verdict

        # Determine final verdict (combine LLM verdict with hard thresholds)
        if llm_verdict == "approved" and quality_score >= 0.55 and lift_percent >= 8:
            critic_verdict = "approved"
            feedback = evaluation.verdict_reason or "Strategy approved."
        elif evaluation.constraint_violations > 0 or llm_verdict == "violation":
            critic_verdict = "violation"
            feedback = evaluation.verdict_reason or "Strategy has constraint violations."
        else:
            critic_verdict = "low_lift"
            feedback = evaluation.verdict_reason or f"Lift {lift_percent}% below threshold or quality insufficient."

        criticism = {
            "quality_score": round(quality_score, 3),
            "lift_assessment": f"{lift_percent}% projected lift",
            "constraint_violations": evaluation.constraint_violations,
            "critical_feedback": evaluation.critical_feedback,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "recommendations": evaluation.recommendations,
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
            "feedback": f"Critique error: {str(e)}",
            "errors": [f"Strategy critic error: {str(e)}"],
            "current_node": "strategy_critic",
        }
