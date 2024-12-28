from typing import Optional

import typer
from typing_extensions import Annotated

from . import get_ai_response


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
