"""Main CLI entry point for the h-cli tool."""

from typing import Any, Callable, Dict, Optional, Tuple

import typer
from click import get_current_context
from rich.console import Console

from h.config import load_config
from h.logger import setup_logger
from h.plugins.git.functions import (
    git_commit_msg_prompt,
    git_commit_msg_prompt_options,
    git_tree,
)

app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments are provided
    context_settings={"help_option_names": ["-h", "--help"]},  # Enable -h flag
)

console = Console()
logger = setup_logger()

# with function itself. and typer options decorator
# commands: Dict[str, Tuple[str, Callable[..., Any]]] = {
#     "git-prompt": (git_commit_msg_prompt, git_commit_msg_prompt_options()),
#     "git-list-files": (git_tree, git_commit_msg_prompt_options()),
# }


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


@git_commit_msg_prompt_options()
@app.command()
def gp(log_count: int = 5, tree_depth: int = 3) -> None:
    """깃 커밋 메시지 프롬프트 생성 및 저장."""
    return git_commit_msg_prompt(log_count=log_count, tree_depth=tree_depth)


@app.command()
def gt() -> None:
    """깃 프로젝트 파일 트리 출력."""
    return git_tree()


if __name__ == "__main__":
    app()
