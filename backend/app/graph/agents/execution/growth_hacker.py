"""
Execution Agent: Growth Hacker
================================
Applies growth frameworks and tactics using Groq (Llama-3).
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

        response = llm.invoke(prompt.format(
            causes=json.dumps(verified_causes),
            constraints=json.dumps(constrained_brief)
        ))

        content = response.content.strip()
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        result = json.loads(content)

        return {
            "agent": "growth_hacker",
            "proposed_tactics": result.get("proposed_tactics", []),
            "experiment_designs": result.get("experiment_designs", []),
            "viral_loops": result.get("viral_loops", []),
            "activation_improvements": result.get("activation_improvements", []),
            "speed_to_impact": result.get("speed_to_impact", {}),
            "framework": "Pirate Metrics (AARRR)",
            "confidence": 0.75,
        }

    except Exception as e:
        return {
            "agent": "growth_hacker",
            "error": str(e),
        }
