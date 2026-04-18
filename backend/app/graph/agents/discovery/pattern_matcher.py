"""
Discovery Agent: Pattern Matcher
==================================
Identifies recurring patterns and user segments using Gemini.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

import os
from typing import Any, List
from pydantic import BaseModel, Field
from app.graph.utils import safe_llm_invoke
from app.graph.state import RetentionGraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


class PatternDef(BaseModel):
    pattern: str
    churn_risk: str
    affected_users: int
    description: str

class UserSegment(BaseModel):
    segment_id: str
    size: int
    retention_rate: float
    characteristics: str

class TopicCluster(BaseModel):
    topic: str
    cluster_size: int

class ChurnSequence(BaseModel):
    sequence: str
    probability: float

class PatternMatcherResult(BaseModel):
    patterns_found: List[PatternDef]
    user_segments: List[UserSegment]
    topic_clusters: List[TopicCluster]
    churn_sequences: List[ChurnSequence]
    pattern_confidence: float

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

        import json
        response = safe_llm_invoke(
            llm, PatternMatcherResult,
            prompt.format(cohorts=json.dumps(behavior_cohorts), features=json.dumps(feature_store)),
            agent_name="PatternMatcher",
        )

        return {
            "agent": "pattern_matcher",
            "patterns_found": [p.model_dump() for p in response.patterns_found],
            "user_segments": [s.model_dump() for s in response.user_segments],
            "topic_clusters": [t.model_dump() for t in response.topic_clusters],
            "churn_sequences": [s.model_dump() for s in response.churn_sequences],
            "pattern_confidence": response.pattern_confidence,
        }

    except Exception as e:
        return {
            "agent": "pattern_matcher",
            "error": str(e),
        }
