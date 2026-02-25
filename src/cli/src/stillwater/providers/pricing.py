"""
Stillwater LLM Model Pricing Table
Version: 1.0.0

All prices are in hundredths of a cent per 1 million tokens (int).
This ensures exact arithmetic with zero float drift.

Example: Claude Sonnet input = 300_00 means $3.00 per 1M input tokens.
         300_00 hundredths-of-cent = 300.00 cents = $3.00

Usage:
    from stillwater.providers.pricing import MODEL_PRICING, estimate_cost

    cost = estimate_cost(input_tokens=1000, output_tokens=500, model="claude-sonnet-4-20250514")
    # Returns cost in hundredths of a cent (int)
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Pricing: hundredths of a cent per 1M tokens
# ---------------------------------------------------------------------------
# Formula: cost_hundredths_cent = (tokens * price_per_1M) // 1_000_000
# All values are int. No float anywhere in the cost path.

MODEL_PRICING: dict[str, dict[str, int]] = {
    # --- Anthropic ---
    "claude-opus-4-20250514": {"input": 1500_00, "output": 7500_00},
    "claude-sonnet-4-20250514": {"input": 300_00, "output": 1500_00},
    "claude-haiku-4-5-20251001": {"input": 80_00, "output": 400_00},

    # --- OpenAI ---
    "gpt-4o": {"input": 250_00, "output": 1000_00},
    "gpt-4o-mini": {"input": 15_00, "output": 60_00},

    # --- Together.ai ---
    "meta-llama/Llama-3.3-70B-Instruct": {"input": 59_00, "output": 59_00},

    # --- Ollama (local, free) ---
    "ollama/*": {"input": 0, "output": 0},
}

# Aliases: map common short names to canonical model IDs
MODEL_ALIASES: dict[str, str] = {
    "claude-opus": "claude-opus-4-20250514",
    "claude-sonnet": "claude-sonnet-4-20250514",
    "claude-haiku": "claude-haiku-4-5-20251001",
    "gpt4o": "gpt-4o",
    "gpt4o-mini": "gpt-4o-mini",
    "llama-70b": "meta-llama/Llama-3.3-70B-Instruct",
    "llama3.3": "meta-llama/Llama-3.3-70B-Instruct",
}


def resolve_model_name(model: str) -> str:
    """Resolve aliases and return canonical model name."""
    return MODEL_ALIASES.get(model, model)


def get_pricing(model: str) -> dict[str, int] | None:
    """
    Get pricing for a model. Returns {"input": int, "output": int} or None.

    Checks exact match first, then aliases, then wildcard patterns like "ollama/*".
    """
    canonical = resolve_model_name(model)

    # Exact match
    if canonical in MODEL_PRICING:
        return MODEL_PRICING[canonical]

    # Wildcard match (e.g. "ollama/*" matches any ollama model)
    for pattern, pricing in MODEL_PRICING.items():
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            if canonical.startswith(prefix) or model.startswith(prefix):
                return pricing

    return None


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> int:
    """
    Estimate cost in hundredths of a cent (int). Uses exact integer arithmetic.

    Args:
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        model: Model name (or alias).

    Returns:
        Cost in hundredths of a cent (int). Returns 0 if model pricing unknown.
    """
    pricing = get_pricing(model)
    if pricing is None:
        return 0

    # Exact integer arithmetic: (tokens * price_per_1M) // 1_000_000
    input_cost = (input_tokens * pricing["input"]) // 1_000_000
    output_cost = (output_tokens * pricing["output"]) // 1_000_000
    return input_cost + output_cost
