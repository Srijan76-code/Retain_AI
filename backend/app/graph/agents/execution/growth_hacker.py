"""
Execution Agent: Growth Hacker
================================
Applies growth frameworks and tactics using Groq (Llama-3).
Called by: strategy_pod_node
"""

from __future__ import annotations

import os
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from app.graph.utils import safe_llm_invoke
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RetentionGraphState

class ProposedTactic(BaseModel):
    name: str
    description: str
    target_metric: str
    expected_lift: float
    implementation_timeline: str
    confidence: float = Field(default=0.8) # Provide default since it's used in calculation

class ExperimentDesign(BaseModel):
    test_name: str
    control: str
    variant: str
    metric: str
    sample_size: int
    duration_days: int

class ActivationImprovement(BaseModel):
    focus: str
    current_step: str
    improvement: str
    estimated_lift: float

class ViralLoop(BaseModel):
    loop: str
    trigger: str
    incentive: str
    estimated_impact: str

class SpeedToImpact(BaseModel):
    quick_wins: List[str]
    medium_term: List[str]
    long_term: List[str]
    prioritization_logic: str

class GrowthHackerResult(BaseModel):
    proposed_tactics: List[ProposedTactic]
    experiment_designs: List[ExperimentDesign]
    activation_improvements: List[ActivationImprovement]
    viral_loops: List[ViralLoop]
    speed_to_impact: SpeedToImpact

def run_growth_hacker(state: RetentionGraphState) -> dict[str, Any]:
    """Generate growth-focused retention strategies using Groq."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        constrained_brief = state.get("constrained_brief", {})

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_2"),
            temperature=0.6,
        )

        prompt = ChatPromptTemplate.from_template(
            """As a Growth Hacker, design high-impact activation and retention experiments for a B2B SaaS product.
            
            Verified Causes of Churn: {causes}
            Constraints: {constraints}
            
            Focus on the Pirate Metrics (AARRR) framework - specifically Activation and Retention loops.
            
            Return ONLY a valid JSON object. No other text. Use this structure:
            {{
                "proposed_tactics": [
                    {{
                        "name": "Activation boost: X",
                        "description": "...",
                        "target_metric": "Day-30 activation rate",
                        "expected_lift": 15.5,
                        "implementation_timeline": "2-3 weeks"
                    }}
                ],
                "experiment_designs": [
                    {{
                        "test_name": "Test_X",
                        "control": "Current experience",
                        "variant": "Enhanced workflow",
                        "metric": "7-day retention",
                        "sample_size": 1000,
                        "duration_days": 14
                    }}
                ],
                "activation_improvements": [
                    {{
                        "focus": "Onboarding",
                        "current_step": "...",
                        "improvement": "...",
                        "estimated_lift": 12.0
                    }}
                ],
                "viral_loops": [
                    {{
                        "loop": "Engagement loop: ...",
                        "trigger": "...",
                        "incentive": "...",
                        "estimated_impact": "..."
                    }}
                ],
                "speed_to_impact": {{
                    "quick_wins": [...],
                    "medium_term": [...],
                    "long_term": [],
                    "prioritization_logic": "..."
                }}
            }}"""
        )

        import json
        response = safe_llm_invoke(
            llm, GrowthHackerResult,
            prompt.format(causes=json.dumps(verified_causes), constraints=json.dumps(constrained_brief)),
            agent_name="GrowthHacker",
        )

        tactics_dump = [t.model_dump() for t in response.proposed_tactics]

        return {
            "agent": "growth_hacker",
            "proposed_tactics": tactics_dump,
            "experiment_designs": [e.model_dump() for e in response.experiment_designs],
            "viral_loops": [v.model_dump() for v in response.viral_loops],
            "activation_improvements": [a.model_dump() for a in response.activation_improvements],
            "speed_to_impact": response.speed_to_impact.model_dump(),
            "framework": "Pirate Metrics (AARRR)",
            "confidence": _avg_confidence(tactics_dump),
        }

    except Exception as e:
        return {
            "agent": "growth_hacker",
            "error": str(e),
        }


def _avg_confidence(items: list) -> float:
    """Compute average confidence from LLM-returned items."""
    scores = [i.get("confidence", 0) for i in items if isinstance(i, dict)]
    return round(sum(scores) / len(scores), 3) if scores else 0.0
