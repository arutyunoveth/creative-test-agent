"""Closed-loop security policy.

Enforces that no data leaves the local environment.
Cloud LLM providers are forbidden by default.
"""

from src.shared.llm.policy import validate_llm_provider

__all__ = ["validate_llm_provider"]
