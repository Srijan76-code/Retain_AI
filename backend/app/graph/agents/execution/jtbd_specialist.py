"""
Execution Agent: JTBD Specialist
==================================
Applies Jobs-To-Be-Done framework using Groq (Llama-3).
Called by: strategy_pod_node
"""

from __future__ import annotations

import os
from typing import Any, List, Literal
from pydantic import BaseModel, Field
from app.graph.state import RetentionGraphState
from app.graph.utils import safe_llm_invoke
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


class IdentifiedJob(BaseModel):
    job_type: str
    description: str
    related_cause: str

class SatisfactionGap(BaseModel):
    job: str
    current_satisfaction: float
    target_satisfaction: float
    gap: float

class ProposedIntervention(BaseModel):
    intervention: str
    job_focus: str
    expected_impact: float
    implementation_effort: str
    confidence: float = Field(default=0.8) # Provide default since it's used in confidence calculation

class JobPriority(BaseModel):
    job_type: str
    description: str
    priority: int

class JTBDResult(BaseModel):
    identified_jobs: List[IdentifiedJob]
    satisfaction_gaps: List[SatisfactionGap]
    proposed_interventions: List[ProposedIntervention]
    job_priority_ranking: List[JobPriority]

def run_jtbd_specialist(state: RetentionGraphState) -> dict[str, Any]:
    """Generate strategies using the JTBD framework via Groq."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        constrained_brief = state.get("constrained_brief", {})

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_1"),
            temperature=0.5,
        )

        prompt = ChatPromptTemplate.from_template(
            """As a JTBD (Jobs-To-Be-Done) specialist, analyze these churn causes and map them to unmet user jobs.

            Verified Causes: {causes}
            Constraints: {constraints}

            For each cause, identify:
            1. Functional job (what does the user need to accomplish?)
            2. Emotional job (how should they feel?)
            3. Social job (how should they be perceived?)

            Then propose interventions that address the most critical jobs.

            Return ONLY a valid JSON object. No other text. Use this structure:
            {{
                "identified_jobs": [
                    {{"job_type": "functional|emotional|social", "description": "...", "related_cause": "..."}}
                ],
                "satisfaction_gaps": [
                    {{"job": "...", "current_satisfaction": 0.4, "target_satisfaction": 0.85, "gap": 0.45}}
                ],
                "proposed_interventions": [
                    {{"intervention": "...", "job_focus": "functional|emotional|social", "expected_impact": 0.15, "implementation_effort": "low|medium|high"}}
                ],
                "job_priority_ranking": [
                    {{"job_type": "...", "description": "...", "priority": 1}}
                ]
            }}"""
        )

        import json
        response = safe_llm_invoke(
            llm, JTBDResult,
            prompt.format(causes=json.dumps(verified_causes), constraints=json.dumps(constrained_brief)),
            agent_name="JTBDSpecialist",
        )

        interventions_dump = [i.model_dump() for i in response.proposed_interventions]

        return {
            "agent": "jtbd_specialist",
            "identified_jobs": [j.model_dump() for j in response.identified_jobs],
            "satisfaction_gaps": [g.model_dump() for g in response.satisfaction_gaps],
            "proposed_interventions": interventions_dump,
            "job_priority_ranking": [r.model_dump() for r in response.job_priority_ranking],
            "framework": "Jobs-to-be-Done",
            "confidence": _avg_confidence(interventions_dump),
        }

    except Exception as e:
        return {
            "agent": "jtbd_specialist",
            "error": str(e),
        }


def _avg_confidence(items: list) -> float:
    """Compute average confidence from LLM-returned items."""
    scores = [i.get("confidence", 0) for i in items if isinstance(i, dict)]
    return round(sum(scores) / len(scores), 3) if scores else 0.0
