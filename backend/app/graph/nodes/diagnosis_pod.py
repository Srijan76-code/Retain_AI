"""
Node 5: Diagnosis Pod
======================
Action:  Parallel analysis via Discovery Agents
Tools:   Forensic Detective, Pattern Matcher, Professional Skeptic
Spawns:  3 discovery agents in parallel
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from app.graph.state import RetentionGraphState
from app.graph.agents.discovery.forensic_detective import run_forensic_detective
from app.graph.agents.discovery.pattern_matcher import run_pattern_matcher
from app.graph.agents.discovery.professional_skeptic import run_professional_skeptic


def diagnosis_pod_node(state: RetentionGraphState) -> dict:
    """Run three Discovery Agents in parallel, then merge findings."""
    try:
        # Run Discovery Agents in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            forensic_future = executor.submit(run_forensic_detective, state)
            pattern_future = executor.submit(run_pattern_matcher, state)

            forensic_output = forensic_future.result()
            pattern_output = pattern_future.result()

        skeptic_output = run_professional_skeptic(state, forensic_output, pattern_output)

        # Merge results into unified diagnosis
        forensic_causes = forensic_output.get("suspected_causes", [])
        forensic_conf = forensic_output.get("confidence_scores", {})

        # Combine findings
        forensic_citations = forensic_output.get("citations", {}) or {}
        retrieved_sources = forensic_output.get("retrieved_sources", []) or []
        source_lookup = {s["id"]: s["source"] for s in retrieved_sources}

        diagnosis_results = {
            "forensic_findings": forensic_output,
            "pattern_findings": pattern_output,
            "skeptic_findings": skeptic_output,
            "merged_hypotheses": [
                {
                    "hypothesis": cause,
                    "confidence": forensic_conf.get(cause, 0.5),
                    "supported_by": ["forensic_detective", "pattern_matcher"],
                    "citations": [
                        {"id": cid, "source": source_lookup.get(cid, cid)}
                        for cid in forensic_citations.get(cause, [])
                    ],
                }
                for cause in forensic_causes[:3]
            ],
            "highest_confidence": max(forensic_conf.values()) if forensic_conf else 0,
            "total_patterns_identified": len(pattern_output.get("patterns_found", [])),
        }

        # Increment discovery attempt counter
        discovery_attempts = state.get("discovery_attempts", 0) + 1

        return {
            "forensic_detective_output": forensic_output,
            "pattern_matcher_output": pattern_output,
            "professional_skeptic_output": skeptic_output,
            "diagnosis_results": diagnosis_results,
            "discovery_attempts": discovery_attempts,
            "current_node": "diagnosis_pod",
        }

    except Exception as e:
        return {
            "forensic_detective_output": {},
            "pattern_matcher_output": {},
            "professional_skeptic_output": {},
            "diagnosis_results": {
                "merged_hypotheses": [],
                "highest_confidence": 0,
            },
            "discovery_attempts": state.get("discovery_attempts", 0) + 1,
            "errors": [*state.get("errors", []), f"Diagnosis pod error: {str(e)}"],
            "current_node": "diagnosis_pod",
        }
