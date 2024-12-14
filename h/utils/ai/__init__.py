from h.utils.ai.base import AIInterface
from h.utils.ai.gemini import GeminiAI
from h.utils.ai.openai import OpenAI

__all__ = [
    "AIInterface",
    "GeminiAI",
    "OpenAI",
]

def get_ai_response(prompt: str) -> str:
    """
    Generates a response from the Gemini AI model.

    Args:
        prompt (str): The input prompt.

    Returns:
        str: The generated text.
    """
    gemini_ai = GeminiAI()
    response = gemini_ai.generate_text(prompt)
    return response