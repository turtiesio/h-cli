"""AI adapters package."""

from typing import Union

from app.core.config import get_config

from .gemini import GeminiAI
from .openai import OpenAIAI


def get_ai_response(prompt: str) -> str:
    """Get AI response for the given prompt."""
    config = get_config()
    if not config.ai_provider:
        raise ValueError("AI provider not configured")

    ai: Union[GeminiAI, OpenAIAI]
    if config.ai_provider == "gemini":
        if not config.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        ai = GeminiAI(config.gemini_api_key)
    elif config.ai_provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        ai = OpenAIAI(config.openai_api_key)
    else:
        raise ValueError(f"Unsupported AI provider: {config.ai_provider}")

    return ai.generate_text(prompt)


__all__ = ["GeminiAI", "OpenAIAI", "get_ai_response"]
