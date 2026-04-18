"""
Node 3: Feature Engineering
=============================
Action:  Compute RFM, LTV, Velocity metrics
Tools:   Pandas, NumPy
Adds:    feature_store
"""

from __future__ import annotations

import duckdb
from app.graph.state import RetentionGraphState


def feature_engineering_node(state: RetentionGraphState) -> dict:
    """Engineer retention-relevant features: RFM, LTV, velocity."""
    try:
        raw_csv_path = state.get("raw_csv_path", "")
        conn = duckdb.connect(":memory:")
        df = conn.execute(f"SELECT * FROM read_csv_auto('{raw_csv_path}')").df()

        feature_store = {
            "rfm_scores": {},
            "ltv_estimates": {},
            "velocity_metrics": {},
            "engagement_cohorts": {},
            "feature_count": 0,
            "feature_list": [],
        }

        # Detect numeric columns for feature engineering
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        # 1. RFM Scores (if relevant columns exist)
        if numeric_cols:
            for col in numeric_cols[:3]:  # Use first 3 numeric columns as proxy
                try:
                    col_mean = df[col].mean()
                    col_std = df[col].std()
                    if col_std > 0:
                        feature_store["rfm_scores"][f"{col}_zscore"] = {
                            "mean": float(col_mean),
                            "std": float(col_std),
                        }
                except:
                    pass

        # 2. Engagement velocity (rate of change)
        for col in numeric_cols[:2]:
            try:
                values = df[col].dropna().values
                if len(values) > 1:
                    velocity = (values[-1] - values[0]) / len(values) if len(values) > 0 else 0
                    feature_store["velocity_metrics"][f"{col}_velocity"] = float(velocity)
            except:
                pass

        # 3. Simple LTV proxy (if monetary column exists)
        if numeric_cols:
            ltv_proxy = df[numeric_cols].sum().sum() / len(df) if len(df) > 0 else 0
            feature_store["ltv_estimates"]["ltv_proxy"] = float(ltv_proxy)

        # 4. Engagement cohorts
        if numeric_cols:
            col_percentiles = df[numeric_cols[0]].quantile([0.25, 0.5, 0.75]).to_dict()
            feature_store["engagement_cohorts"] = {
                "low": float(col_percentiles.get(0.25, 0)),
                "medium": float(col_percentiles.get(0.5, 0)),
                "high": float(col_percentiles.get(0.75, 0)),
            }

        feature_store["feature_list"] = list(feature_store.keys())
        feature_store["feature_count"] = len(feature_store["feature_list"])

        return {
            "feature_store": feature_store,
            "current_node": "feature_engineering",
        }

    except Exception as e:
        return {
            "feature_store": {
                "rfm_scores": {},
                "ltv_estimates": {},
                "velocity_metrics": {},
                "feature_count": 0,
            },
            "errors": [*state.get("errors", []), f"Feature engineering error: {str(e)}"],
            "current_node": "feature_engineering",
        }
