"""
Node 8: Adaptive HITL (Human-in-the-Loop)
==========================================
Action:  Generate targeted clarification questions
Tools:   LLM Chat Agent
Adds:    human_clarification, hitl_questions
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json


def adaptive_hitl_node(state: RetentionGraphState) -> dict:
    """Generate and ask targeted clarification questions."""
    try:
        constrained_brief = state.get("constrained_brief", {})
        feasible_interventions = constrained_brief.get("feasible_interventions", [])
        input_context = state.get("input_context", {})

        # Generate smart questions based on the brief
        hitl_questions = generate_questions(feasible_interventions, input_context)

        # Structure for human response (to be filled by user)
        human_clarification = {
            "questions_asked": hitl_questions,
            "responses": state.get("human_clarification", {}).get("responses", {}),
            "clarification_status": "pending" if not state.get("human_clarification") else "provided",
        }

        # If no human response yet, this node pauses for input
        # The graph will have an `interrupt_before` checkpoint here

        return {
            "hitl_questions": hitl_questions,
            "human_clarification": human_clarification,
            "current_node": "adaptive_hitl",
        }

    except Exception as e:
        return {
            "hitl_questions": [
                "What is your primary retention metric?",
                "What is your total budget for retention initiatives?",
                "What is your implementation timeline?",
            ],
            "human_clarification": {
                "questions_asked": [],
                "responses": {},
                "clarification_status": "error",
            },
            "errors": [*state.get("errors", []), f"HITL error: {str(e)}"],
            "current_node": "adaptive_hitl",
        }


def generate_questions(feasible_interventions: list, context: dict) -> list[str]:
    """Generate 2-3 targeted clarification questions."""
    try:
        industry = context.get("industry", "SaaS")
        company_size = context.get("company_size", "unknown")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
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

        try:
            questions = json.loads(response.content)
            return questions if isinstance(questions, list) else default_questions()
        except:
            return default_questions()

    except:
        return default_questions()


def default_questions() -> list[str]:
    """Fallback questions if LLM fails."""
    return [
        "What is your target retention improvement percentage over the next 6 months?",
        "Which customer segment should we prioritize (e.g., SMB, Enterprise, New)?",
        "What is your preferred implementation approach (quick wins vs. comprehensive overhaul)?",
    ]
