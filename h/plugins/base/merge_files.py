import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console

from h.utils import vscode_utils
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger

logger = get_logger(__name__)


IGNORED_FILES = ["uv.lock", "package.lock"]

def add_merge_files(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def merge_files(
        directory: str = typer.Option(
            ".", "--dir", "-d", help="Directory to merge files from"
        ),
    ) -> None:
        """Merges all source files under a specified directory into a temporary file."""
        console = Console()
        merged_content = ""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--directory", directory],
                capture_output=True,
                text=True,
                check=True,
            )
            git_files = result.stdout.splitlines()

            for file_path_str in git_files:
                if file_path_str.split("/")[-1] in IGNORED_FILES:
                    logger.info(f"Ignoring file: {file_path_str} (ignored)")
                    continue

                file_path = Path(directory) / file_path_str
                with open(file_path, "r") as f:
                    merged_content += f"## File: {file_path}\n"
                    merged_content += f.read() + "\n"

            temp_file = create_temp_file(
                filename="merged_files.txt", content=merged_content
            )
            console.print(
                f"\n[bold]Merged Files File: [blue]{temp_file}[/blue][/bold]\n\n"
            )
            vscode_utils.open_file_with_vscode(temp_file)
        except Exception as e:
            logger.error("merge_files.failed", error=str(e))
            console.print("\n[red]Error:[/red] Failed to merge files.")
            raise typer.Exit(1)
