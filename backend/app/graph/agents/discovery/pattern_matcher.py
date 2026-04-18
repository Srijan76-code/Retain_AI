"""
Discovery Agent: Pattern Matcher
==================================
Identifies recurring patterns and user segments using Gemini.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

import os
import json
import re
from app.graph.utils import extract_llm_text
from typing import Any
from app.graph.state import RetentionGraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def run_pattern_matcher(state: RetentionGraphState) -> dict[str, Any]:
    """Discover recurring retention/churn patterns via LLM analysis."""
    try:
        feature_store = state.get("feature_store", {})
        behavior_cohorts = state.get("behavior_cohorts", [])

        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY_2"),
            temperature=0.2,
        )

        prompt = ChatPromptTemplate.from_template(
            """Analyze these user behavior cohorts and features to identify recurring churn patterns and segments.
            
            Behavior Cohorts: {cohorts}
            Feature Store Data: {features}
            
            Identify:
            1. High-risk user segments.
            2. Feature-based patterns (e.g., specific feature adoption gaps).
            3. Common "churn sequences" (steps users take before leaving).
            
            Return ONLY a valid JSON object. No other text. Use this structure:
            {{
                "patterns_found": [
                    {{"pattern": "pattern_name", "churn_risk": "high/med/low", "affected_users": 100, "description": "..."}}
                ],
                "user_segments": [
                    {{"segment_id": "...", "size": 100, "retention_rate": 0.8, "characteristics": "..."}}
                ],
                "topic_clusters": [
                    {{"topic": "...", "cluster_size": 10}}
                ],
                "churn_sequences": [
                    {{"sequence": "step1 -> step2 -> churn", "probability": 0.85}}
                ],
                "pattern_confidence": 0.85
            }}"""
        )

        response = llm.invoke(prompt.format(
            cohorts=json.dumps(behavior_cohorts),
            features=json.dumps(feature_store)
        ))

        content = extract_llm_text(response.content)
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        result = json.loads(content)

        return {
            "agent": "pattern_matcher",
            "patterns_found": result.get("patterns_found", []),
            "user_segments": result.get("user_segments", []),
            "topic_clusters": result.get("topic_clusters", []),
            "churn_sequences": result.get("churn_sequences", []),
            "pattern_confidence": result.get("pattern_confidence", 0.72),
        }

    except Exception as e:
        return {
            "agent": "pattern_matcher",
            "error": str(e),
        }
