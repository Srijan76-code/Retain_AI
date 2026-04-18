"""
Execution Agent: Unit Economist
=================================
Analyses unit economics implications using Groq (Llama-3).
Called by: strategy_pod_node
"""

from __future__ import annotations

import os
import json
import re
from typing import Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RetentionGraphState


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

        response = llm.invoke(prompt.format(
            causes=json.dumps(verified_causes),
            ltv=ltv_proxy,
            constraints=json.dumps(constrained_brief)
        ))

        content = response.content.strip()
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        result = json.loads(content)

        return {
            "agent": "unit_economist",
            "proposed_interventions": result.get("proposed_interventions", []),
            "roi_projections": result.get("roi_projections", {}),
            "cac_ltv_impact": result.get("cac_ltv_impact", {}),
            "cost_estimates": result.get("cost_estimates", {}),
            "top_roi_intervention": result.get("top_roi_intervention", {}),
            "framework": "Unit Economics / LTV-CAC",
            "confidence": 0.72,
        }

    except Exception as e:
        return {
            "agent": "unit_economist",
            "error": str(e),
        }
