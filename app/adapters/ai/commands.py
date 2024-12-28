from typing import Optional

import typer  # type: ignore
from typing_extensions import Annotated

from . import get_ai_response


def add_ai(app: typer.Typer, name: str):
    @app.command(name=name, help="Ask a question to an AI model")
    def ai(
        question: Annotated[
            Optional[str], typer.Argument(help="The question to ask the AI model")
        ] = None,
    ):
        if question is None:
            question = typer.prompt("What is your question?")

        if question:
            system_prompt = "You are a helpful assistant. Please provide a short and concise response for a developer. "
            print(get_ai_response(system_prompt + question))
