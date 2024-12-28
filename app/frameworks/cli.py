from typing import Optional
import typer
from click import get_current_context
from rich.console import Console

from app.core.config import load_config
from app.frameworks.logger import setup_logger
from app.adapters.ai import add_ai
from app.adapters.git import add_git_clone, add_git_commit_msg_prompt, add_git_tree
from importlib.metadata import version

console = Console()
logger = setup_logger()


def get_context_data() -> dict:
    """Get common context data used across commands.

    Returns:
        Dict containing logger, config, and console instances.
    """
    return {
        "config": load_config(),
        "logger": logger,
        "console": console,
    }


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"h-cli version: {version('h-cli')}")
        raise typer.Exit()


def add_main(app: typer.Typer, name: str) -> None:
    @app.callback()
    def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Enable verbose logging"
        ),
    ) -> None:
        """Personal productivity CLI tool with plugin architecture."""
        if verbose:
            logger.debug("Verbose logging enabled")

        # Initialize context data
        context_data = get_context_data()
        context_data["verbose"] = verbose

        # Set context for the current command
        get_current_context().obj = context_data
        logger.debug("cli.initialized", verbose=verbose)


def add_version(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def version() -> None:
        """Show version information."""
        version_str = version('h-cli')
        logger.info("cli.version", version=version_str)
        console.print(f"h-cli version: {version_str}")


app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

add_main(app, "main")
add_version(app, "version")
add_git_commit_msg_prompt(app, "gp")
add_git_tree(app, "gt")
add_git_clone(app, "gc")
add_ai(app, "ai")

if __name__ == "__main__":
    app()
