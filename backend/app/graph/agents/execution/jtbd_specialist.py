"""
Execution Agent: JTBD Specialist
==================================
Applies Jobs-To-Be-Done framework using Groq (Llama-3).
Called by: strategy_pod_node
"""

from __future__ import annotations

import os
import json
import re
from typing import Any
from app.graph.state import RetentionGraphState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


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

        response = llm.invoke(prompt.format(
            causes=json.dumps(verified_causes),
            constraints=json.dumps(constrained_brief)
        ))

        content = response.content.strip()
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        result = json.loads(content)

        return {
            "agent": "jtbd_specialist",
            "identified_jobs": result.get("identified_jobs", []),
            "satisfaction_gaps": result.get("satisfaction_gaps", []),
            "proposed_interventions": result.get("proposed_interventions", []),
            "job_priority_ranking": result.get("job_priority_ranking", []),
            "framework": "Jobs-to-be-Done",
            "confidence": 0.68,
        }

    except Exception as e:
        return {
            "agent": "jtbd_specialist",
            "error": str(e),
        }
