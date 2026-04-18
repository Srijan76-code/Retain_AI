"""
Discovery Agent: Professional Skeptic
=======================================
Challenges assumptions and stress-tests hypotheses using LLM-powered
adversarial reasoning.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

import os
import json
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from app.graph.state import RetentionGraphState
from app.graph.utils import safe_llm_invoke
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class CounterArgument(BaseModel):
    hypothesis: str
    counter_argument: str
    strength: str

class AlternativeExplanation(BaseModel):
    hypothesis: str
    alternative: str
    testability: str

class BiasFlag(BaseModel):
    issue: str
    risk: str
    recommendation: str

class OverallQuality(BaseModel):
    forensic_quality: float
    pattern_quality: float
    combined_confidence: float
    recommendation: str

class SkepticResult(BaseModel):
    counter_arguments: List[CounterArgument]
    robustness_scores: Dict[str, float]
    alternative_explanations: List[AlternativeExplanation]
    bias_flags: List[BiasFlag]
    overall_quality: OverallQuality

def run_professional_skeptic(
    state: RetentionGraphState,
    forensic_findings: dict[str, Any],
    pattern_findings: dict[str, Any],
) -> dict[str, Any]:
    """Adversarial review of hypotheses and findings using LLM reasoning."""
    try:
        forensic_causes = forensic_findings.get("suspected_causes", [])
        forensic_confidence = forensic_findings.get("confidence_scores", {})
        pattern_sequences = pattern_findings.get("churn_sequences", [])
        pattern_found = pattern_findings.get("patterns_found", [])

        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY_1"),
            temperature=0.4,
        )

        skeptic_prompt = ChatPromptTemplate.from_template(
            """You are a Professional Skeptic reviewing churn analysis findings.
Your job is to challenge assumptions, find flaws, and stress-test hypotheses.

## Forensic Findings
Suspected causes: {causes}
Confidence scores: {confidence}

## Pattern Findings
Churn sequences: {sequences}
Patterns found: {patterns}

For EACH suspected cause, provide:
1. A specific counter-argument (not generic — reference the actual cause)
2. A robustness score (0.0-1.0) based on how well-supported the hypothesis is
3. One alternative explanation

Also flag any cognitive biases (confirmation bias, survivorship bias, overfitting).

Return as JSON:
{{
  "counter_arguments": [{{"hypothesis": "...", "counter_argument": "...", "strength": "low|medium|high"}}],
  "robustness_scores": {{"cause_name": 0.XX}},
  "alternative_explanations": [{{"hypothesis": "...", "alternative": "...", "testability": "low|medium|high"}}],
  "bias_flags": [{{"issue": "...", "risk": "low|medium|high", "recommendation": "..."}}],
  "overall_quality": {{"forensic_quality": 0.XX, "pattern_quality": 0.XX, "combined_confidence": 0.XX, "recommendation": "..."}}
}}"""
        )

        response = safe_llm_invoke(
            llm, SkepticResult,
            skeptic_prompt.format(
                causes=json.dumps(forensic_causes),
                confidence=json.dumps(forensic_confidence),
                sequences=json.dumps(pattern_sequences[:3]),
                patterns=json.dumps([p.get("pattern", "") if isinstance(p, dict) else "" for p in pattern_found[:5]]),
            ),
            agent_name="ProfessionalSkeptic",
        )

        return {
            "agent": "professional_skeptic",
            "counter_arguments": [c.model_dump() for c in response.counter_arguments][:5],
            "bias_flags": [b.model_dump() for b in response.bias_flags],
            "robustness_scores": response.robustness_scores,
            "alternative_explanations": [a.model_dump() for a in response.alternative_explanations][:3],
            "overall_quality_assessment": response.overall_quality.model_dump(),
            "approval_status": "conditional_proceed",
        }

    except Exception as e:
        return {
            "agent": "professional_skeptic",
            "error": str(e),
        }
