"""
Shared utilities for LLM response handling.
=============================================
"""

from __future__ import annotations


def extract_llm_text(content) -> str:
    """Safely extract text from LLM response content.
    
    Handles cases where response.content is:
    - A plain string
    - A list of content blocks (common with newer Gemini models)
    - A list of dicts with 'text' keys
    """
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(part.get("text", ""))
        return "".join(parts).strip()
    return str(content).strip()


def get_churn_column(df) -> str | None:
    """Robustly identify the binary churn column in a DataFrame."""
    churn_candidates = [c for c in df.columns if 'churn' in c.lower()]
    for c in churn_candidates:
        if df[c].dtype in ['int64', 'float64'] and set(df[c].dropna().unique()).issubset({0, 1, 0.0, 1.0}):
            return c
    # Fall back to any column explicitly named is_churned or churned
    return next((c for c in churn_candidates if 'is_churn' in c.lower() or c.lower() == 'churned'), None)
