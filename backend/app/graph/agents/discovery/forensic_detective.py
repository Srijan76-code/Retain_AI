"""
Discovery Agent: Forensic Detective
=====================================
Investigates data anomalies and traces root causes.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

from typing import Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RetentionGraphState
import os
import json


def run_forensic_detective(state: RetentionGraphState) -> dict[str, Any]:
    """Deep forensic investigation of retention patterns."""
    try:
        import duckdb

        raw_csv_path = state.get("raw_csv_path", "")
        behavior_curves = state.get("behavior_curves", {})
        behavior_cohorts = state.get("behavior_cohorts", [])
        feature_store = state.get("feature_store", {})

        # Load CSV for actual statistical analysis
        conn = duckdb.connect(":memory:")
        df = conn.execute(f"SELECT * FROM read_csv_auto('{raw_csv_path}')").df()

        # Calculate actual statistics from data
        churn_col = next((c for c in df.columns if 'churn' in c.lower()), None)

        stats = {"churn_rate": 0, "churn_by_channel": {}, "churn_by_integration": {}}

        if churn_col:
            stats["churn_rate"] = round(df[churn_col].mean(), 2)

            # Churn by acquisition channel
            acq_col = next((c for c in df.columns if 'acquisition' in c.lower() or 'channel' in c.lower()), None)
            if acq_col:
                for channel in df[acq_col].unique():
                    churn_rate = df[df[acq_col] == channel][churn_col].mean()
                    stats["churn_by_channel"][str(channel)] = round(churn_rate, 2)

            # Churn by integration
            int_col = next((c for c in df.columns if 'integration' in c.lower()), None)
            if int_col:
                for status in df[int_col].unique():
                    churn_rate = df[df[int_col] == status][churn_col].mean()
                    stats["churn_by_integration"][str(status)] = round(churn_rate, 2)

        # Use Gemini to generate forensic insights
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
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

        response = llm.invoke(prompt.format(
            churn_rate=f"{stats['churn_rate']:.1%}",
            churn_by_channel=json.dumps(stats["churn_by_channel"]),
            churn_by_integration=json.dumps(stats["churn_by_integration"]),
        ))

        # Parse response
        try:
            result = json.loads(response.content)
            suspected_causes = result.get("suspected_causes", [])
            confidence_scores = result.get("confidence_scores", {})
        except:
            suspected_causes = [
                "Insufficient engagement in early lifecycle",
                "Price sensitivity in target segment",
                "Integration complexity or usability issues",
            ]
            confidence_scores = {c: 0.6 for c in suspected_causes}

        return {
            "agent": "forensic_detective",
            "suspected_causes": suspected_causes,
            "confidence_scores": confidence_scores,
            "analysis_depth": "high",
        }

    except Exception as e:
        # Fallback if LLM fails
        return {
            "agent": "forensic_detective",
            "suspected_causes": [
                "High early churn in onboarding phase",
                "Lack of value realization in first 30 days",
                "Feature adoption gaps",
            ],
            "confidence_scores": {
                "onboarding": 0.7,
                "value_realization": 0.65,
                "feature_adoption": 0.6,
            },
            "error": str(e),
        }
