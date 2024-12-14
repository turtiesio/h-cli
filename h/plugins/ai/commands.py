import typer
from typing_extensions import Annotated
from h.utils.ai import get_ai_response

def add_ai(app: typer.Typer, name: str):
    @app.command(name=name, help="Ask a question to an AI model")
    def ai(
        question: Annotated[
            str, typer.Argument(help="The question to ask the AI model")
        ] = None,
    ):
        if question is None:
            question = typer.prompt("What is your question?")
        
        response = get_ai_response(question)
        print(response)