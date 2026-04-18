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


def safe_llm_invoke(llm, schema, prompt_text: str, agent_name: str = "Unknown"):
    """Invoke LLM with structured output, falling back to raw JSON parsing.
    
    Strategy:
      1. Try with_structured_output() — cleanest path (function calling)
      2. If that returns None, fall back to raw invoke + manual JSON extraction
      3. Validate through Pydantic either way
    
    This guarantees a valid Pydantic model or raises a clear exception.
    """
    import json
    import re

    # ── Attempt 1: Structured output (function calling) ──────────────
    try:
        structured_llm = llm.with_structured_output(schema)
        result = structured_llm.invoke(prompt_text)
        if result is not None:
            return result
    except Exception:
        pass  # Fall through to raw parsing

    # ── Attempt 2: Raw invoke + JSON extraction ──────────────────────
    raw_response = llm.invoke(prompt_text)
    content = extract_llm_text(raw_response.content)

    # Strip markdown code fences
    content = re.sub(r'^```(?:json)?\s*', '', content.strip())
    content = re.sub(r'\s*```\s*$', '', content.strip())

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"[{agent_name}] LLM produced neither valid structured output "
            f"nor parseable JSON. Raw content: {content[:300]}..."
        ) from e

    return schema(**data)
