"""AI adapters package."""

from typing import Optional, Union
import typer
from typing_extensions import Annotated

from app.core.config import get_config
from .gemini import GeminiAI
from .openai import OpenAIAI


def get_ai_response(prompt: str) -> str:
    """Get AI response for the given prompt."""
    config = get_config()
    
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


def add_ai(app: typer.Typer, name: str) -> None:
    @app.command(name=name, help="Ask a question to an AI model")
    def ai(  # type: ignore[misc]
        question: Annotated[
            Optional[str], typer.Argument(help="The question to ask the AI model")
        ] = None,
    ) -> None:
        if question is None:
            question = typer.prompt("What is your question?")

        if question:
            system_prompt = "You are a helpful assistant. Please provide a short and concise response for a developer. "
            print(get_ai_response(system_prompt + question))
        return None


__all__ = ["GeminiAI", "OpenAIAI", "get_ai_response", "add_ai"]
