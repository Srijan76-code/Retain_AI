"""
Node 2: Data Audit
===================
Action:  Health & schema checks
Tools:   Pandas
Adds:    data_quality_score, data_quality_logs
"""

from __future__ import annotations
import pandas as pd
from app.graph.state import RetentionGraphState

def data_audit_node(state: RetentionGraphState) -> dict:
    """
    Run data-quality checks on the normalized DataFrame.
    """
    raw = state.get("normalized_df")
    if not raw:
        return {
            "data_quality_score": 0.0,
            "data_quality_logs": ["Audit failed: Missing normalized_df"],
            "current_node": "data_audit"
        }

    # Convert serialized list-of-dicts back to DataFrame
    df = pd.DataFrame(raw)

    logs = []

    # Check for empty dataframe
    if df.empty:
        logs.append("Critical: DataFrame is empty.")
        return {"data_quality_score": 0.0, "data_quality_logs": logs, "current_node": "data_audit"}

    # Basic missing value check
    null_count = df.isnull().sum().sum()
    total_cells = df.size
    null_ratio = null_count / total_cells if total_cells > 0 else 1.0
    
    logs.append(f"Audit complete: {null_count} null cells detected ({null_ratio:.2%})")
    
    # Simplistic score: 1.0 if no nulls, scales down to 0
    score = 1.0 - (null_ratio * 10) # Heavy penalty for nulls
    score = max(0.0, min(1.0, score))

    if score < 0.8:
        logs.append("Warning: Data quality score below threshold.")
    else:
        logs.append("Data quality audit PASSED.")

    return {
        "data_quality_score": score,
        "data_quality_logs": logs,
        "current_node": "data_audit",
    }
