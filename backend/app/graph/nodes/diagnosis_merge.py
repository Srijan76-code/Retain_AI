"""
Node 5c: Diagnosis Merge
==========================
Runs the Professional Skeptic on merged findings from
Forensic Detective + Pattern Matcher, then produces
the final diagnosis_results.
"""

from __future__ import annotations

from app.graph.state import RetentionGraphState
from app.graph.agents.discovery.professional_skeptic import run_professional_skeptic


def diagnosis_merge_node(state: RetentionGraphState) -> dict:
    """Merge Discovery Agent outputs, run skeptic, produce diagnosis."""
    try:
        forensic_output = state.get("forensic_detective_output", {})
        pattern_output = state.get("pattern_matcher_output", {})

        # Run skeptic on the merged findings
        skeptic_output = run_professional_skeptic(state, forensic_output, pattern_output)

        # Build merged hypotheses from forensic causes
        forensic_causes = forensic_output.get("suspected_causes", [])
        forensic_conf = forensic_output.get("confidence_scores", {})

        diagnosis_results = {
            "forensic_findings": forensic_output,
            "pattern_findings": pattern_output,
            "skeptic_findings": skeptic_output,
            "merged_hypotheses": [
                {
                    "hypothesis": cause,
                    "confidence": forensic_conf.get(cause, 0.5),
                    "supported_by": ["forensic_detective", "pattern_matcher"],
                }
                for cause in forensic_causes[:3]
            ],
            "highest_confidence": max(forensic_conf.values()) if forensic_conf else 0,
            "total_patterns_identified": len(pattern_output.get("patterns_found", [])),
        }

        discovery_attempts = state.get("discovery_attempts", 0) + 1

        return {
            "professional_skeptic_output": skeptic_output,
            "diagnosis_results": diagnosis_results,
            "discovery_attempts": discovery_attempts,
            "current_node": "diagnosis_merge",
        }

    except Exception as e:
        return {
            "diagnosis_results": {"error": str(e)},
            "discovery_attempts": state.get("discovery_attempts", 0) + 1,
            "errors": [*state.get("errors", []), f"Diagnosis merge error: {str(e)}"],
            "current_node": "diagnosis_merge",
        }
