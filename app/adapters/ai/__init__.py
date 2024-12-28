"""AI adapters package."""

from app.core.config import get_config

from .gemini import GeminiAI
from .openai import OpenAIAI


def get_ai_response(prompt: str) -> str:
    """Get AI response for the given prompt."""
    config = get_config()
    if config.ai_provider == "gemini":
        ai = GeminiAI(config.gemini_api_key)
    elif config.ai_provider == "openai":
        ai = OpenAIAI(config.openai_api_key)
    else:
        raise ValueError(f"Unsupported AI provider: {config.ai_provider}")

    return ai.generate_text(prompt)


__all__ = ["GeminiAI", "OpenAIAI", "get_ai_response"]
