import fnmatch
import os
import subprocess
from pathlib import Path
from typing import List, Optional

import typer

from app.frameworks.logger import setup_logger as get_logger
from app.tools import vscode_utils
from app.tools.file_utils import (
    create_temp_file,
    is_binary_file,
    read_file,
    should_exclude_file,
    write_file,
)

logger = get_logger(__name__)

IGNORED_FILES = [
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    ".gitignore",
    ".yarn",
    ".terraform.lock.hcl",
]
IGNORED_EXTENSIONS = [".svg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp"]


def get_git_tracked_files() -> List[Path]:
    """Get a list of files tracked by Git in the current directory."""
    try:
        # Get both staged and unstaged files
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [Path(file) for file in result.stdout.splitlines()]
    except subprocess.CalledProcessError:
        return []


def merge_files(
    exclude_patterns: Optional[List[str]] = None,
    additional_files: Optional[List[Path]] = None,
    include_docs: bool = False,  # New parameter
) -> str:
    """
    Merge all files tracked by Git and additional files into a single string.
    Exclude binary files and files matching the exclude patterns.
    """
    if exclude_patterns is None:
        exclude_patterns = []
    if additional_files is None:
        additional_files = []

    merged_content = ""

    # Merge Git-tracked files
    git_files = get_git_tracked_files()
    for file_path in git_files:
        if any(seg in (IGNORED_FILES + exclude_patterns) for seg in file_path.parts):
            logger.info(f"Ignoring file: {file_path}")
            continue

        if should_exclude_file(
            file_path, exclude_patterns, include_docs
        ) or is_binary_file(file_path):
            continue

        try:
            content = read_file(file_path)
            merged_content += f"## File: {file_path}\n{content}\n"
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    # Merge additional files
    for file_path in additional_files:
        if should_exclude_file(
            file_path, exclude_patterns, include_docs
        ) or is_binary_file(file_path):
            continue

        try:
            content = read_file(file_path)
            merged_content += f"## File: {file_path}\n{content}\n"
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    return merged_content


def add_merge_files(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def merge_files_command(
        exclude: List[str] = typer.Option(
            [], "--exclude", "-e", help="Glob patterns to exclude"
        ),
        files: List[Path] = typer.Option(
            [], "--file", "-f", help="Additional files to merge"
        ),
        output: Optional[Path] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
        docs: bool = typer.Option(  # New flag
            False, "--docs", help="Include Markdown files in the merge"
        ),
    ) -> None:
        """Merge files tracked by Git and additional files."""
        seperator = "-" * 10

        merged_content = (
            "\n\n\n"
            + seperator
            + "Merged Files"
            + seperator
            + "\n\n\n"
            + merge_files(
                exclude_patterns=exclude,
                additional_files=files,
                include_docs=docs,  # Pass the flag value
            )
        )

        if output:
            write_file(output, merged_content)
            logger.info(f"Merged content written to {output}")
        else:
            # Create temp file and open in VS Code
            temp_file = create_temp_file(
                filename="merged_files.txt", content=merged_content
            )
            logger.info(f"Merged content available at {temp_file}")
            vscode_utils.open_file_with_vscode(temp_file)
