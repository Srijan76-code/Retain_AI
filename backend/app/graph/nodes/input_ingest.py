"""
Node 1: Input Ingest
=====================
Action:  Normalize diverse CSV schemas using DuckDB
Tools:   DuckDB
Adds:    input_context, input_constraints
"""

from __future__ import annotations

import duckdb
from app.graph.state import RetentionGraphState


def input_ingest_node(state: RetentionGraphState) -> dict:
    """Load CSV and normalize to standard customer schema."""
    try:
        raw_csv_path = state.get("raw_csv_path", "")
        questionnaire = state.get("questionnaire", {})

        # Load CSV with DuckDB (auto-detects schema)
        conn = duckdb.connect(":memory:")
        df = conn.execute(f"SELECT * FROM read_csv_auto('{raw_csv_path}')").df()

        # Detect key columns dynamically (case-insensitive search)
        cols_lower = {col.lower(): col for col in df.columns}

        customer_id_col = next((cols_lower[k] for k in cols_lower if 'id' in k or 'user' in k), None)
        tenure_col = next((cols_lower[k] for k in cols_lower if 'tenure' in k or 'months' in k), None)
        usage_col = next((cols_lower[k] for k in cols_lower if 'usage' in k or 'logins' in k), None)
        support_col = next((cols_lower[k] for k in cols_lower if 'support' in k or 'tickets' in k), None)
        plan_col = next((cols_lower[k] for k in cols_lower if 'plan' in k or 'contract' in k), None)

        input_context = {
            "source": raw_csv_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "detected_columns": {
                "customer_id": customer_id_col,
                "tenure": tenure_col,
                "usage": usage_col,
                "support": support_col,
                "plan": plan_col,
            },
            "business_context": questionnaire.get("business_context", ""),
            "industry": questionnaire.get("industry", ""),
            "company_size": questionnaire.get("size", ""),
        }

        input_constraints = {
            "time_range": questionnaire.get("time_range", "last_12_months"),
            "product_lines": questionnaire.get("product_lines", []),
            "market_segment": questionnaire.get("market_segment", ""),
            "budget_constraints": questionnaire.get("budget", ""),
            "legal_constraints": questionnaire.get("legal_constraints", []),
        }

        return {
            "normalized_df": df.to_dict(orient="records"),  # serialize for state
            "input_context": input_context,
            "input_constraints": input_constraints,
            "current_node": "input_ingest",
            "retry_count": state.get("retry_count", 0),
        }

    except Exception as e:
        return {
            "errors": [*state.get("errors", []), f"Input ingest error: {str(e)}"],
            "current_node": "input_ingest",
            "retry_count": state.get("retry_count", 0) + 1,
        }
