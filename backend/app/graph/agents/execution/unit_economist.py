"""
Execution Agent: Unit Economist
=================================
Analyses unit economics implications using Groq (Llama-3).
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

class ProposedInterventionUE(BaseModel):
    intervention: str
    confidence: float
    estimated_cost: str
    cost_usd: float
    expected_roi: float
    rationale: str

class ROIProjection(BaseModel):
    year_1_revenue_impact: float
    implementation_cost: float
    roi_percent: float
    payback_months: float

class CACLTVImpact(BaseModel):
    current_ltv: float
    projected_ltv: float
    ltv_improvement_pct: float

class CostEstimate(BaseModel):
    implementation: float
    ongoing_monthly: float
    time_to_value_weeks: float

class TopROIIntervention(BaseModel):
    intervention: str
    expected_roi: float

class UnitEconomistResult(BaseModel):
    proposed_interventions: List[ProposedInterventionUE]
    roi_projections: Dict[str, ROIProjection]
    cac_ltv_impact: Dict[str, CACLTVImpact]
    cost_estimates: Dict[str, CostEstimate]
    top_roi_intervention: TopROIIntervention

def run_unit_economist(state: RetentionGraphState) -> dict[str, Any]:
    """Generate strategies optimised for unit economics using Groq."""
    try:
        verified_causes = state.get("verified_root_causes", [])
        constrained_brief = state.get("constrained_brief", {})
        feature_store = state.get("feature_store", {})
        ltv_proxy = feature_store.get("ltv_estimates", {}).get("ltv_proxy", 1000)

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_1"),
            temperature=0.3,
        )

        prompt = ChatPromptTemplate.from_template(
            """As a Unit Economist, analyze these churn causes and propose ROI-positive interventions for a B2B SaaS company.
            
            Verified Causes: {causes}
            Current LTV Proxy: ${ltv}
            Constraints: {constraints}
            
            Focus on:
            1. Estimating implementation cost (low/medium/high).
            2. Calculating Year-1 ROI based on realistic retention lift.
            3. Payback period in months.
            
            Return ONLY a valid JSON object. No other text. Use this structure:
            {{
                "proposed_interventions": [
                    {{"intervention": "step name", "confidence": 0.85, "estimated_cost": "low", "cost_usd": 5000, "expected_roi": 120.5, "rationale": "..."}}
                ],
                "roi_projections": {{
                    "cause_name": {{
                        "year_1_revenue_impact": 50000,
                        "implementation_cost": 5000,
                        "roi_percent": 120.5,
                        "payback_months": 2.5
                    }}
                }},
                "cac_ltv_impact": {{
                    "cause_name": {{
                        "current_ltv": 1000,
                        "projected_ltv": 1200,
                        "ltv_improvement_pct": 20.0
                    }}
                }},
                "cost_estimates": {{
                    "cause_name": {{
                        "implementation": 5000,
                        "ongoing_monthly": 400,
                        "time_to_value_weeks": 4
                    }}
                }},
                "top_roi_intervention": {{"intervention": "...", "expected_roi": 150.0}}
            }}"""
        )

        import json
        response = safe_llm_invoke(
            llm, UnitEconomistResult,
            prompt.format(causes=json.dumps(verified_causes), ltv=ltv_proxy, constraints=json.dumps(constrained_brief)),
            agent_name="UnitEconomist",
        )

        interventions_dump = [i.model_dump() for i in response.proposed_interventions]

        return {
            "agent": "unit_economist",
            "proposed_interventions": interventions_dump,
            "roi_projections": {k: v.model_dump() for k, v in response.roi_projections.items()},
            "cac_ltv_impact": {k: v.model_dump() for k, v in response.cac_ltv_impact.items()},
            "cost_estimates": {k: v.model_dump() for k, v in response.cost_estimates.items()},
            "top_roi_intervention": response.top_roi_intervention.model_dump(),
            "framework": "Unit Economics / LTV-CAC",
            "confidence": _avg_confidence(interventions_dump),
        }

    except Exception as e:
        return {
            "agent": "unit_economist",
            "error": str(e),
        }


def _avg_confidence(interventions: list) -> float:
    """Compute average confidence from LLM-returned interventions."""
    scores = [i.get("confidence", 0) for i in interventions if isinstance(i, dict)]
    return round(sum(scores) / len(scores), 3) if scores else 0.0
