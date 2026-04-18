"""
Node 8: Adaptive HITL (Human-in-the-Loop)
==========================================
Action:  Generate targeted clarification questions
Tools:   LLM Chat Agent
Adds:    human_clarification, hitl_questions
"""

from __future__ import annotations

import os
import json
from app.graph.utils import extract_llm_text
from app.graph.state import RetentionGraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def adaptive_hitl_node(state: RetentionGraphState) -> dict:
    """Generate and ask targeted clarification questions."""
    try:
        constrained_brief = state.get("constrained_brief", {})
        feasible_interventions = constrained_brief.get("feasible_interventions", [])
        input_context = state.get("input_context", {})

        industry = input_context.get("industry", "SaaS")
        company_size = input_context.get("company_size", "unknown")

        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY_2"),
            temperature=0.3,
        )

        prompt = ChatPromptTemplate.from_template(
            """Given these potential retention interventions and context, generate 2-3 specific, actionable questions
            that would help clarify priorities or constraints:

            Interventions: {interventions}
            Industry: {industry}
            Company Size: {size}

            Generate exactly 2-3 questions. Format as a JSON list.
            Return ONLY the JSON list of questions, no other text."""
        )

        intervention_names = [i.get("cause", "") for i in feasible_interventions[:3]]
        response = llm.invoke(prompt.format(
            interventions=", ".join(intervention_names) if intervention_names else "Multiple retention strategies",
            industry=industry,
            size=company_size,
        ))

        raw_content = extract_llm_text(response.content)
        hitl_questions = json.loads(raw_content)
        if not isinstance(hitl_questions, list):
            raise ValueError("LLM did not return a list of questions")

        human_clarification = {
            "questions_asked": hitl_questions,
            "responses": state.get("human_clarification", {}).get("responses", {}),
            "clarification_status": "pending" if not state.get("human_clarification") else "provided",
        }

        return {
            "hitl_questions": hitl_questions,
            "human_clarification": human_clarification,
            "current_node": "adaptive_hitl",
        }

    except Exception as e:
        return {
            "human_clarification": {
                "questions_asked": [],
                "responses": {},
                "clarification_status": "error",
            },
            "errors": [*state.get("errors", []), f"HITL error: {str(e)}"],
            "current_node": "adaptive_hitl",
        }
