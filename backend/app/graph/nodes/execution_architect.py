"""
Node 12: Execution Architect
===============================
Action:  Generate LLM-powered final playbook from real pipeline data
Tools:   Groq LLM (Llama 3.3 70B)
Adds:    final_playbook
"""

from __future__ import annotations

import os
import json
import re
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RetentionGraphState


def execution_architect_node(state: RetentionGraphState) -> dict:
    """Produce the final execution playbook using LLM with real pipeline data."""
    try:
        # ── Gather all real data from the pipeline ───────────────────────
        verified_root_causes = state.get("verified_root_causes", [])
        merged_strategies = state.get("strategy_outputs", {}).get("merged_strategies", [])
        lift_percent = state.get("lift_percent", 0)
        input_context = state.get("input_context", {})
        constrained_brief = state.get("constrained_brief", {})
        simulations = state.get("simulations", {})
        criticism = state.get("criticism", {})

        # Strategy agent outputs
        economist_output = state.get("unit_economist_output", {})
        jtbd_output = state.get("jtbd_specialist_output", {})
        growth_output = state.get("growth_hacker_output", {})

        # ── Initialize Groq LLM ─────────────────────────────────────────
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_3"),
            temperature=0.3,
        )

        prompt = ChatPromptTemplate.from_template(
            """You are a senior retention strategist creating a final execution playbook for a real company.

## Company Context
Industry: {industry}
Business Model: {business_model}
Company Stage: {company_stage}
Target Churn Rate: {target_churn}
Goal: {goal}

## Verified Root Causes (from data analysis)
{root_causes}

## Strategies Proposed (from specialist agents)
Unit Economist: {economist}
JTBD Specialist: {jtbd}
Growth Hacker: {growth}

## Merged Strategy Recommendations
{strategies}

## Simulation Results
Projected Lift: {lift}%
Simulations: {simulations}

## Constraints
{constraints}

## Critic Feedback
{criticism}

---

Based on ALL of the above real data, create a detailed execution playbook.

For EACH problem identified, structure it as:

1. **Problem**: What specific problem was discovered (reference the actual root cause)
2. **Solution**: How exactly to solve it (reference the actual strategy proposed)
3. **Retention Impact**: How much retention improvement this specific solution can drive (use real numbers from the simulation/lift data)
4. **Effort & Steps**: Step-by-step implementation plan with effort estimates

Return ONLY a valid JSON object with this exact structure:
{{
    "title": "Retention Optimization Playbook",
    "executive_summary": {{
        "total_problems_identified": 3,
        "total_projected_retention_lift": "{lift}%",
        "estimated_timeline": "90 days",
        "estimated_budget": "$XX,XXX",
        "confidence_level": "High/Medium/Low"
    }},
    "problems_and_solutions": [
        {{
            "priority": 1,
            "problem": {{
                "title": "Short problem title",
                "description": "Detailed description of the problem based on actual data",
                "affected_segment": "Which customer segment is affected",
                "current_impact": "How much churn this problem causes (use real data)"
            }},
            "solution": {{
                "title": "Short solution title",
                "description": "Detailed explanation of how to solve this",
                "framework_used": "Which strategy framework (Unit Economics / JTBD / Growth)",
                "key_actions": ["Action 1", "Action 2", "Action 3"]
            }},
            "retention_impact": {{
                "estimated_lift_percent": 5.0,
                "estimated_users_retained": 50,
                "estimated_revenue_impact": "$50,000",
                "confidence": 0.85,
                "time_to_impact": "30 days"
            }},
            "implementation_steps": [
                {{
                    "step": 1,
                    "action": "What to do",
                    "owner": "Team/Role responsible",
                    "effort": "low/medium/high",
                    "timeline": "Week 1-2",
                    "deliverable": "What gets produced",
                    "dependencies": ["Any blockers"]
                }}
            ]
        }}
    ],
    "30_60_90_roadmap": {{
        "phase_1_30_days": {{
            "theme": "Foundation & Quick Wins",
            "goals": ["Goal 1", "Goal 2"],
            "key_milestones": ["Milestone 1", "Milestone 2"],
            "expected_lift": "X%"
        }},
        "phase_2_60_days": {{
            "theme": "Scale & Optimize",
            "goals": ["Goal 1", "Goal 2"],
            "key_milestones": ["Milestone 1", "Milestone 2"],
            "expected_lift": "X%"
        }},
        "phase_3_90_days": {{
            "theme": "Measure & Iterate",
            "goals": ["Goal 1", "Goal 2"],
            "key_milestones": ["Milestone 1", "Milestone 2"],
            "expected_lift": "X%"
        }}
    }},
    "success_metrics": [
        {{
            "metric": "Metric name",
            "current_value": "X%",
            "target_value": "Y%",
            "measurement_method": "How to measure",
            "review_frequency": "Weekly/Monthly"
        }}
    ],
    "risks_and_mitigations": [
        {{
            "risk": "What could go wrong",
            "probability": "low/medium/high",
            "mitigation": "How to prevent it",
            "contingency": "What to do if it happens"
        }}
    ],
    "resource_requirements": {{
        "team": ["Role 1", "Role 2"],
        "technology": ["Tool 1", "Tool 2"],
        "budget_breakdown": {{
            "people": "$X",
            "technology": "$X",
            "marketing": "$X",
            "total": "$X"
        }}
    }}
}}"""
        )

        root_causes_str = json.dumps(verified_root_causes, indent=2)
        strategies_str = json.dumps(merged_strategies, indent=2)

        response = llm.invoke(prompt.format(
            industry=input_context.get("industry", "Unknown"),
            business_model=input_context.get("business_model", "Unknown"),
            company_stage=input_context.get("company_stage", "Unknown"),
            target_churn=input_context.get("target_churn_rate", "Unknown"),
            goal=input_context.get("goal", "Reduce churn"),
            root_causes=root_causes_str,
            economist=json.dumps(economist_output, indent=2)[:1500],
            jtbd=json.dumps(jtbd_output, indent=2)[:1500],
            growth=json.dumps(growth_output, indent=2)[:1500],
            strategies=strategies_str,
            lift=lift_percent,
            simulations=json.dumps(simulations, indent=2)[:1000] if simulations else "No simulation data",
            constraints=json.dumps(constrained_brief, indent=2)[:1000] if constrained_brief else "No constraints",
            criticism=json.dumps(criticism, indent=2)[:500] if criticism else "No critic feedback",
        ))

        content = response.content.strip()
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        playbook = json.loads(content)

        # Enrich with metadata
        playbook["created_date"] = datetime.now().isoformat()
        playbook["company"] = input_context.get("industry", "SaaS")
        playbook["estimated_total_lift"] = round(lift_percent, 1)

        return {
            "final_playbook": playbook,
            "playbook_status": "approved_for_execution",
            "current_node": "execution_architect",
        }

    except Exception as e:
        return {
            "final_playbook": {"error": str(e)},
            "playbook_status": "error",
            "errors": [*state.get("errors", []), f"Execution architect error: {str(e)}"],
            "current_node": "execution_architect",
        }
