"""Main CLI entry point for the h-cli tool."""

from typing import Any, Dict, Optional, List
import typer
from rich.console import Console
import os
import fnmatch
from h.config import load_config
from h.logger import setup_logger
from click import get_current_context
from h.plugins.git.git_plugin_functions import get_git_commands, get_template_content, open_in_vscode, prompt, list_files

app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments are provided
    context_settings={"help_option_names": ["-h", "--help"]},  # Enable -h flag
)

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
    get_current_context().obj = context_data
    logger.debug("cli.initialized", verbose=verbose)


@app.command()
def version() -> None:
    """Show version information."""
    from h import __version__

    logger.info("cli.version", version=__version__)
    console.print(f"h-cli version: {__version__}")

@app.command("git-prompt")
def git_prompt_command(
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
):
    """커밋 메시지 생성을 위한 프롬프트 생성."""
    return prompt(log_count=log_count, tree_depth=tree_depth)

@app.command("git-list-files")
def git_list_files_command():
    """List files in the git repository."""
    return list_files()

if __name__ == "__main__":
    app()
