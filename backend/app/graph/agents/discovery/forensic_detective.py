"""
Discovery Agent: Forensic Detective
=====================================
Investigates data anomalies and traces root causes.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

import os
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from app.graph.utils import get_churn_column, safe_llm_invoke
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RetentionGraphState


class DetectiveResult(BaseModel):
    suspected_causes: List[str]
    confidence_scores: Dict[str, float]

def run_forensic_detective(state: RetentionGraphState) -> dict[str, Any]:
    """Deep forensic investigation of retention patterns."""
    try:
        import duckdb

        raw_csv_path = state.get("raw_csv_path", "")

        # Load CSV for actual statistical analysis
        conn = duckdb.connect(":memory:")
        df = conn.execute(f"SELECT * FROM read_csv_auto('{raw_csv_path}')").df()

        # Calculate actual statistics from data
        churn_col = get_churn_column(df)

        stats = {"churn_rate": 0, "churn_by_channel": {}, "churn_by_integration": {}}

        if churn_col:
            stats["churn_rate"] = round(df[churn_col].mean(), 2)

            acq_col = next((c for c in df.columns if 'acquisition' in c.lower() or 'channel' in c.lower()), None)
            if acq_col:
                for channel in df[acq_col].unique():
                    churn_rate = df[df[acq_col] == channel][churn_col].mean()
                    stats["churn_by_channel"][str(channel)] = round(churn_rate, 2)

            int_col = next((c for c in df.columns if 'integration' in c.lower()), None)
            if int_col:
                for status in df[int_col].unique():
                    churn_rate = df[df[int_col] == status][churn_col].mean()
                    stats["churn_by_integration"][str(status)] = round(churn_rate, 2)

        # Use Gemini to generate forensic insights
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY_1"),
            temperature=0.3,
        )

        prompt = ChatPromptTemplate.from_template(
            """Analyze this B2B SaaS retention data and identify root causes of churn:

            Overall Churn Rate: {churn_rate}
            Churn by Acquisition Channel: {churn_by_channel}
            Churn by Integration Status: {churn_by_integration}

            Based on these statistics, identify 3 root causes with confidence (0.7-1.0 range).
            Format as JSON: {{"suspected_causes": ["cause1", "cause2", "cause3"], "confidence_scores": {{"cause1": 0.85, ...}}}}
            """
        )

        import json
        response = safe_llm_invoke(
            llm, DetectiveResult,
            prompt.format(
                churn_rate=f"{stats['churn_rate']:.1%}",
                churn_by_channel=json.dumps(stats['churn_by_channel']),
                churn_by_integration=json.dumps(stats['churn_by_integration']),
            ),
            agent_name="ForensicDetective",
        )

        suspected_causes = response.suspected_causes
        confidence_scores = response.confidence_scores

        return {
            "agent": "forensic_detective",
            "suspected_causes": suspected_causes,
            "confidence_scores": confidence_scores,
            "statistical_evidence": stats,
            "analysis_depth": "high",
        }

    except Exception as e:
        return {
            "agent": "forensic_detective",
            "error": str(e),
        }
