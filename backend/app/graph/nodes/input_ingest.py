"""
Node 1: Input Ingest
=====================
Action:  Normalize diverse schemas (CSV, JSON, Parquet, etc.)
Tools:   DuckDB, Pydantic
Adds:    input_context, input_constraints
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def input_ingest_node(state: RetentionGraphState) -> dict:
    """
    Ingest raw CSV + questionnaire and normalize into a unified schema.

    TODO: Replace dummy logic with actual implementation:
      - Load raw CSV via DuckDB
      - Validate questionnaire with Pydantic models
      - Extract context (company, product, time range) and constraints
    """
    # ── Dummy implementation — replace with actual code ──────────────
    input_context = {
        "source": state.get("raw_csv_path", ""),
        "schema_detected": "placeholder",
        "row_count": 0,
        "column_count": 0,
    }
    input_constraints = {
        "time_range": "last_12_months",
        "product_line": "all",
        "constraints_from_questionnaire": state.get("questionnaire", {}),
    }

    return {
        "input_context": input_context,
        "input_constraints": input_constraints,
        "current_node": "input_ingest",
    }
