"""Main CLI entry point for the h-cli tool."""

from typing import Any, Dict

import typer
from rich.console import Console

from h.config import load_config
from h.core.commands import add_main, add_version
from h.logger import setup_logger
from h.plugins.git.functions import add_git_commit_msg_prompt, add_git_tree

app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments are provided
    context_settings={"help_option_names": ["-h", "--help"]},  # Enable -h flag
)

add_main(app, "main")
add_version(app, "version")

add_git_commit_msg_prompt(app, "gp")
add_git_tree(app, "gt")


if __name__ == "__main__":
    app()
