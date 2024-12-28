from typing import Any, Dict, Optional

import typer
from click import get_current_context
from rich.console import Console

from app import __version__
from app.core.config import load_config
from app.frameworks.logger import setup_logger

console = Console()
logger = setup_logger()


def get_context_data() -> Dict[str, Any]:
    """Get common context data used across commands.

    Returns:
        Dict containing logger, config, and console instances.
    """
    return {
        "config": load_config(),
        "logger": logger,  # Return the logger directly
        "console": console,
    }


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:

        console.print(f"h-cli version: {__version__}")
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
        logger.info("cli.version", version=__version__)
        console.print(f"h-cli version: {__version__}")
