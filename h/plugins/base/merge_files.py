import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console

from h.utils import vscode_utils
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger

logger = get_logger(__name__)


IGNORED_FILES = ["uv.lock", "package.lock", "yarn.lock"]

def add_merge_files(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def merge_files(
        directory: str = typer.Option(
            ".", "--dir", "-d", help="Directory to merge files from"
        ),
        exclude: list[str] = typer.Option(
            [], "--exclude", "-e", help="Files and directories to exclude"
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
                segments = file_path_str.split("/")
                
                if any(seg in (IGNORED_FILES + exclude) for seg in segments):
                    logger.info(f"Ignoring file: {file_path_str}")
                    continue
                
                file_path = Path(directory) / file_path_str
                
                try:
                    with open(file_path, "r") as f:
                        merged_content += f"## File: {file_path}\n"
                        merged_content += f.read() + "\n"
                except UnicodeDecodeError:
                    logger.warn(f"Skipping file due to encoding error: {file_path}")
                    continue

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
