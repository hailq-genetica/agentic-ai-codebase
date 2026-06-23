"""Configuration loading and model constants."""

import yaml

# Combined context window (input + output) limits (in tokens).
# Source: OpenAI API docs and Anthropic docs
# https://platform.openai.com/docs/models
# https://docs.anthropic.com/en/docs/about-claude/models
MODEL_CONTEXT_LIMITS = {
    # Direct OpenAI (platform.openai.com)
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4o-2024-08-06": 128_000,
    "o1": 200_000,
    "o1-mini": 128_000,
    # Azure OpenAI / OpenAI Responses API
    "gpt-5": 400_000,
    "o4-mini-0416": 128_000,
    # Anthropic Claude models
    "claude-3-5-sonnet-20241022": 200_000,
    "claude-3-5-haiku-20241022": 200_000,
    "claude-3-opus-20240229": 200_000,
    "claude-3-sonnet-20240229": 200_000,
    "claude-3-haiku-20240307": 200_000,
    "claude-4-sonnet-latest": 200_000,
    "claude-opus-4-6": 200_000,
    "claude-opus-4-7": 200_000,
    "claude-opus-4-8": 200_000,
    "claude-sonnet-4-6": 200_000,
}

# Max output tokens per response (subset of context window)
MODEL_OUTPUT_LIMITS = {
    # Direct OpenAI
    "gpt-4o": 16_384,
    "gpt-4o-mini": 16_384,
    "gpt-4o-2024-08-06": 16_384,
    "o1": 100_000,
    "o1-mini": 65_536,
    # Azure OpenAI / OpenAI
    "gpt-5": 128_000,
    "o4-mini-0416": 16_384,
    # Anthropic Claude models (all support up to 8K standard, can request higher)
    "claude-3-5-sonnet-20241022": 8192,
    "claude-3-5-haiku-20241022": 8192,
    "claude-3-opus-20240229": 4096,
    "claude-3-sonnet-20240229": 4096,
    "claude-3-haiku-20240307": 4096,
    "claude-4-sonnet-latest": 8192,
    "claude-opus-4-6": 16384,
    "claude-opus-4-7": 64000,
    "claude-opus-4-8": 64000,
    "claude-sonnet-4-6": 16384,
}

# Estimated tokens per image at different detail levels
# These remain heuristic, not official guarantees.
IMAGE_TOKENS_ESTIMATE = {
    "low": 85,
    "high": 765,  # Conservative upper bound for typical image inputs
    "auto": 765,
}


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        dict: Parsed configuration
    """
    with open(config_path) as f:
        return yaml.safe_load(f)
