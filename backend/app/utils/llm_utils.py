"""Shared utilities for parsing LLM responses."""

import json
import re
import logging

logger = logging.getLogger(__name__)

_JSON_RE = re.compile(r"\{[\s\S]*\}")


def extract_json(response: str, context: str = "") -> dict:
    """
    Extract the first JSON object from an LLM response string.

    Args:
        response: Raw text returned by the LLM.
        context:  Short label for log messages (e.g. "[CONTEMPLATE]").

    Returns:
        Parsed dict.

    Raises:
        ValueError: If no JSON block is found or JSON is malformed.
    """
    match = _JSON_RE.search(response)
    if not match:
        logger.error("%s No JSON found in LLM response (first 500 chars):\n%s", context, response[:500])
        raise ValueError(f"{context} LLM response contained no JSON object")

    try:
        return json.loads(match.group())
    except json.JSONDecodeError as exc:
        logger.error("%s JSON parse failed: %s\nRaw match:\n%s", context, exc, match.group()[:500])
        raise ValueError(f"{context} Failed to parse JSON from LLM response: {exc}") from exc
