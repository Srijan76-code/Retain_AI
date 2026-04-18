"""
Node 5a: Forensic Detective (Discovery Agent)
===============================================
Runs as a standalone LangGraph node for native parallel execution.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from app.graph.agents.discovery.forensic_detective import run_forensic_detective


def forensic_detective_node(state: RetentionGraphState) -> dict:
    """Run the Forensic Detective agent."""
    output = run_forensic_detective(state)
    return {
        "forensic_detective_output": output,
        "current_node": "forensic_detective",
    }
