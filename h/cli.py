"""Main CLI application for h-cli.

This module serves as the entry point for the h-cli tool.
It provides a plugin-based architecture for extending functionality.
"""
import os
from typing import Optional

import typer
import structlog

from .plugins.git import app as git_app

# Initialize logger
logger = structlog.get_logger()

def create_app() -> typer.Typer:
    """Create and configure the main CLI application.
    
    Returns:
        Configured Typer application
    """
    app = typer.Typer(
        help="h-cli: A productivity CLI tool",
        no_args_is_help=True,
    )
    
    # Add git commands with shorter alias
    app.add_typer(git_app, name="gp")
    
    return app

def get_app() -> typer.Typer:
    """Get the main CLI application instance.
    
    This is the main entry point for the CLI tool.
    
    Returns:
        Configured Typer application
    """
    app = create_app()
    
    @app.callback()
    def main(
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ) -> None:
        """h-cli: A productivity CLI tool.
        
        This tool provides various productivity enhancements through a plugin system.
        """
        # Configure logging based on verbosity
        log_level = "DEBUG" if verbose else "INFO"
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
        )
        
        # Store logger in context for plugins to use
        typer.get_current_context().obj = {"logger": logger}
    
    return app

app = get_app()

if __name__ == "__main__":
    app()
"""Main CLI entry point for the h-cli tool."""

from typing import Any, Dict, Optional

import typer
from rich.console import Console

from h.config import load_config
from h.logger import setup_logger
from h.plugins.git import app as git_app

app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments are provided
    context_settings={"help_option_names": ["-h", "--help"]},  # Enable -h flag
)

# Add plugins
app.add_typer(git_app, name="gp")

console = Console()
logger = setup_logger()


def get_context_data() -> Dict[str, Any]:
    """Get common context data used across commands.

    Returns:
        Dict containing logger, config, and console instances.
    """
    return {
        "config": load_config(),
        "logger": logger.bind(),  # Create a new bound logger
        "console": console,
    }


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from h import __version__
        console.print(f"h-cli version: {__version__}")
        raise typer.Exit()


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
    from click import get_current_context
    get_current_context().obj = context_data
    logger.debug("cli.initialized", verbose=verbose)


@app.command()
def version() -> None:
    """Show version information."""
    from h import __version__

    logger.info("cli.version", version=__version__)
    console.print(f"h-cli version: {__version__}")


if __name__ == "__main__":
    app()
