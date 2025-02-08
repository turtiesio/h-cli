import os
import subprocess
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from app.adapters.git.git_commands import GitCommands
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
    "pnpm-lock.yaml",
    "yarn.lock",
    ".gitignore",
    ".yarn",
    ".terraform.lock.hcl",
]
IGNORED_EXTENSIONS = [".svg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp"]


def get_git_tracked_files(directory: Path) -> List[Path]:
    """Get a list of files tracked by Git in the specified directory."""
    try:
        # Use -c core.quotepath=false to prevent escaping non-ASCII characters
        result = subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            cwd=directory,
        )

        return [Path(file) for file in result.stdout.split("\n") if file]
    except subprocess.CalledProcessError:
        return []


def merge_files(
    directory: Path,
    exclude_patterns: Optional[List[str]] = None,
    additional_files: Optional[List[Path]] = None,
    include_docs: bool = False,
    char_count: bool = False,
) -> str:
    """
    Merge all files tracked by Git and additional files into a single string.
    Exclude binary files and files matching the exclude patterns.
    If char_count is True, prepend each file name with its character count.

    Args:
        directory (Path): The directory to process files from
        exclude_patterns (Optional[List[str]]): Patterns to exclude from processing
        additional_files (Optional[List[Path]]): Additional files to include
        include_docs (bool): Whether to include documentation files
        char_count (bool): Whether to prepend each file name with its character count

    Returns:
        str: The merged content of all processed files
    """
    if exclude_patterns is None:
        exclude_patterns = []
    if additional_files is None:
        additional_files = []

    merged_content = ""

    # Get directory structure, respecting exclusions
    git = GitCommands(logger)
    git_files = get_git_tracked_files(directory)
    filtered_files = []

    for file_path in git_files:
        full_path = directory / file_path
        if any(seg in (IGNORED_FILES + exclude_patterns) for seg in full_path.parts):
            logger.info(f"Ignoring file: {full_path}")
            continue

        if should_exclude_file(
            full_path, exclude_patterns, include_docs
        ) or is_binary_file(full_path):
            continue

        filtered_files.append(file_path)

    # Generate directory structure from filtered files
    directory_lines = []
    for file_path in filtered_files:
        full_path = directory / file_path
        if char_count:
            try:
                content = read_file(full_path)
                count = len(content)
                line = f"[{count} chars] {file_path}"
            except Exception as e:
                logger.error(f"Error reading file {full_path}: {e}")
                line = f"[0 chars] {file_path}"
        else:
            line = str(file_path)
        directory_lines.append(line)

    directory_structure = "\n".join(directory_lines)
    merged_content += f"## Directory Structure\n{directory_structure}\n\n"

    # Merge Git-tracked files
    for file_path in filtered_files:
        full_path = directory / file_path
        try:
            content = read_file(full_path)
            char_count_str = f"[{len(content)} chars] " if char_count else ""
            merged_content += f"## File: {char_count_str}{file_path}\n{content}\n"
        except Exception as e:
            logger.error(f"Error processing file {full_path}: {e}")

    # Merge additional files
    for file_path in additional_files:
        if not file_path.is_absolute():
            file_path = directory / file_path

        if should_exclude_file(
            file_path, exclude_patterns, include_docs
        ) or is_binary_file(file_path):
            continue

        try:
            content = read_file(file_path)
            char_count_str = f"[{len(content)} chars] " if char_count else ""
            merged_content += f"## File: {char_count_str}{file_path}\n{content}\n"
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
        docs: bool = typer.Option(
            False, "--docs", help="Include Markdown files in the merge"
        ),
        directory: Annotated[
            Path,
            typer.Option(
                "--dir",
                "-d",
                help="Directory to run merge under",
                file_okay=False,
                exists=True,
                resolve_path=True,
            ),
        ] = Path("."),
        char_count: bool = typer.Option(
            False,
            "-c",
            "--char-count",
            help="Prepend each file name with its character count",
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
                directory=directory,
                exclude_patterns=exclude,
                additional_files=files,
                include_docs=docs,
                char_count=char_count,
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
