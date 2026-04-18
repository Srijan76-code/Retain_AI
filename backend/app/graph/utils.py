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
