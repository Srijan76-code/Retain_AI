"""
Node 4: Behavioral Map
========================
Action:  Survival curves & behavioral cohorts
Tools:   DuckDB, Pandas
Adds:    behavior_curves, behavior_cohorts
"""

from __future__ import annotations

import duckdb
from app.graph.state import RetentionGraphState
from app.graph.utils import get_churn_column


def behavioral_map_node(state: RetentionGraphState) -> dict:
    """Build behavioral models: survival curves and cohort segmentation."""
    try:
        raw_csv_path = state.get("raw_csv_path", "")
        conn = duckdb.connect(":memory:")
        df = conn.execute(f"SELECT * FROM read_csv_auto('{raw_csv_path}')").df()

        behavior_curves = {
            "survival_curve": {},
            "retention_by_period": {},
            "drop_off_points": [],
            "churn_probability": 0.0,
        }

        behavior_cohorts = []

        # Extract numeric column for tenure/time proxy
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if numeric_cols:
            tenure_col = numeric_cols[0]
            tenure_values = df[tenure_col].dropna().values

            if len(tenure_values) > 0:
                # Simple survival curve: % of users retained at each period
                sorted_tenure = sorted(tenure_values)
                max_tenure = max(sorted_tenure) if sorted_tenure else 1

                for period in range(0, int(max_tenure) + 1, max(1, int(max_tenure) // 5)):
                    retained = sum(1 for t in tenure_values if t >= period)
                    retention_rate = retained / len(tenure_values) if len(tenure_values) > 0 else 0
                    behavior_curves["survival_curve"][f"month_{period}"] = round(retention_rate, 3)
                    behavior_curves["retention_by_period"][f"period_{period}"] = round(retention_rate, 3)

                # Identify drop-off points (biggest retention drops)
                retention_rates = list(behavior_curves["survival_curve"].values())
                for i in range(1, len(retention_rates)):
                    drop = retention_rates[i-1] - retention_rates[i]
                    if drop > 0.1:  # More than 10% drop
                        behavior_curves["drop_off_points"].append({
                            "period": i,
                            "drop_percent": round(drop * 100, 1),
                        })

                # Churn probability (inverse of final survival)
                final_retention = retention_rates[-1] if retention_rates else 1.0
                behavior_curves["churn_probability"] = round(1 - final_retention, 3)

        # Create behavioral cohorts with real retention rates from data
        churn_col = get_churn_column(df)
        if numeric_cols:
            col_data = df[numeric_cols[0]].dropna()
            if len(col_data) > 0:
                quantile_25 = col_data.quantile(0.25)
                quantile_75 = col_data.quantile(0.75)

                # Calculate actual retention per cohort using churn data
                low_mask = col_data < quantile_25
                med_mask = (col_data >= quantile_25) & (col_data < quantile_75)
                high_mask = col_data >= quantile_75

                for cohort_id, mask, label in [
                    ("low_engagement", low_mask, "Low activity"),
                    ("medium_engagement", med_mask, "Moderate activity"),
                    ("high_engagement", high_mask, "High activity"),
                ]:
                    cohort_size = int(mask.sum())
                    # Calculate real retention rate from churn column if available
                    if churn_col and cohort_size > 0:
                        cohort_churn = df.loc[mask.index[mask], churn_col].mean()
                        retention_rate = round(1.0 - cohort_churn, 3)
                    else:
                        retention_rate = None  # No churn data to calculate from

                    behavior_cohorts.append({
                        "cohort_id": cohort_id,
                        "size": cohort_size,
                        "retention_rate": retention_rate,
                        "characteristics": label,
                        "engagement_range": {
                            "min": round(float(df.loc[mask.index[mask], numeric_cols[0]].min()), 2) if cohort_size > 0 else 0,
                            "max": round(float(df.loc[mask.index[mask], numeric_cols[0]].max()), 2) if cohort_size > 0 else 0,
                        },
                    })

        return {
            "behavior_curves": behavior_curves,
            "behavior_cohorts": behavior_cohorts,
            "current_node": "behavioral_map",
        }

    except Exception as e:
        return {
            "behavior_curves": {"error": str(e)},
            "behavior_cohorts": [],
            "errors": [f"Behavioral map error: {str(e)}"],
            "current_node": "behavioral_map",
        }
