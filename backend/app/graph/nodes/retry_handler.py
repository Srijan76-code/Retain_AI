"""
Retry Handler
==============
Triggered when Data Audit (Node 2) score < threshold.
Requests better data from the user and loops back to Node 1.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState


def retry_handler_node(state: RetentionGraphState) -> dict:
    """
    Handle data-quality failure by requesting better data.

    TODO: Replace dummy logic with actual implementation:
      - Compile specific data-quality issues from data_quality_logs
      - Generate a human-readable message explaining what's wrong
      - Request re-upload or data corrections from the user
      - Once new data arrives, flow re-enters at Node 1 (Input Ingest)
    """
    # ── Dummy implementation — replace with actual code ──────────────
    return {
        "errors": [
            *state.get("errors", []),
            f"Data quality score {state.get('data_quality_score', 0.0)} "
            f"below threshold. Requesting better data.",
        ],
        "retry_count": state.get("retry_count", 0) + 1,
        "current_node": "retry_handler",
    }
