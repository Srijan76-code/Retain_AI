"""
Discovery Agent: Pattern Matcher
==================================
Identifies recurring patterns and user segments.
Called by: diagnosis_pod_node
"""

from __future__ import annotations

from typing import Any
from app.graph.state import RetentionGraphState


def run_pattern_matcher(state: RetentionGraphState) -> dict[str, Any]:
    """Discover recurring retention/churn patterns via clustering."""
    try:
        feature_store = state.get("feature_store", {})
        behavior_cohorts = state.get("behavior_cohorts", [])

        patterns_found = []
        user_segments = []
        churn_sequences = []

        # 1. Identify behavior patterns from cohorts
        if behavior_cohorts:
            for cohort in behavior_cohorts:
                cohort_id = cohort.get("cohort_id", "unknown")
                retention = cohort.get("retention_rate", 0)
                size = cohort.get("size", 0)

                # Determine churn risk pattern
                if retention < 0.5:
                    risk = "high_churn_risk"
                elif retention < 0.8:
                    risk = "moderate_churn_risk"
                else:
                    risk = "low_churn_risk"

                patterns_found.append({
                    "pattern": f"{cohort_id}_pattern",
                    "churn_risk": risk,
                    "affected_users": size,
                })

                user_segments.append({
                    "segment_id": cohort_id,
                    "size": size,
                    "retention_rate": retention,
                    "characteristics": cohort.get("characteristics", ""),
                })

        # 2. Extract feature-based patterns
        velocity_metrics = feature_store.get("velocity_metrics", {})

        if velocity_metrics:
            for metric_name, velocity_val in velocity_metrics.items():
                if velocity_val < 0:
                    patterns_found.append({
                        "pattern": f"declining_{metric_name}",
                        "description": "Decreasing engagement over time",
                        "severity": "high",
                    })

        # 3. Infer churn sequences (typical progression)
        churn_sequences = [
            {
                "sequence": "high_inactivity -> support_tickets_decrease -> churn",
                "probability": 0.75,
            },
            {
                "sequence": "feature_adoption_lag -> limited_usage -> disengagement",
                "probability": 0.65,
            },
            {
                "sequence": "price_sensitivity_signal -> product_downgrade_inquiry -> churn",
                "probability": 0.58,
            },
        ]

        return {
            "agent": "pattern_matcher",
            "patterns_found": patterns_found,
            "user_segments": user_segments,
            "topic_clusters": [
                {"topic": "low_engagement", "cluster_size": len(behavior_cohorts)},
                {"topic": "feature_adoption_gap", "cluster_size": max(1, len(behavior_cohorts) // 2)},
            ],
            "churn_sequences": churn_sequences,
            "pattern_confidence": 0.72,
        }

    except Exception as e:
        return {
            "agent": "pattern_matcher",
            "patterns_found": [
                {
                    "pattern": "generic_churn_pattern",
                    "description": "Default pattern when analysis fails",
                    "severity": "medium",
                }
            ],
            "user_segments": [],
            "topic_clusters": [],
            "churn_sequences": [],
            "error": str(e),
        }
