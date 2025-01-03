import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from structlog import BoundLogger

from app.frameworks.logger import setup_logger as get_logger
from app.tools import vscode_utils
from app.tools.file_utils import create_temp_file

if TYPE_CHECKING:
    from structlog import BoundLogger

logger = get_logger(__name__)


IGNORED_FILES = ["uv.lock", "package-lock.json", "yarn.lock", ".gitignore", ".yarn"]
IGNORED_EXTENSIONS = [".svg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp"]

def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary by reading its first few thousand bytes
    and looking for null bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if the file appears to be binary, False otherwise
    """
    try:
        chunk_size = 8192  # Read 8kb at a time
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            
        # Files with null bytes are usually binary
        if b'\x00' in chunk:
            return True
            
        # Try to decode as text - if it fails, likely binary
        try:
            chunk.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
            
    except Exception as e:
        logger.warning(f"Error checking if file is binary {file_path}: {str(e)}")
        return True  # Assume binary if we can't check properly

def process_file(file_path: Path, merged_content: str, logger: BoundLogger) -> str:
    """Process a single file and append its content to merged_content.
    
    Args:
        file_path: Path to the file
        merged_content: Current merged content
        logger: Logger instance
        
    Returns:
        Updated merged content
    """
    try:
        if not file_path.exists():
            logger.warning(f"File not found, skipping: {file_path}")
            return merged_content
            
        # Skip files with ignored extensions
        if any(file_path.name.lower().endswith(ext) for ext in IGNORED_EXTENSIONS):
            logger.info(f"Skipping file with ignored extension: {file_path}")
            return merged_content
            
        # Skip binary files
        if is_binary_file(file_path):
            logger.info(f"Skipping binary file: {file_path}")
            return merged_content
            
        with open(file_path, "r") as f:
            merged_content += f"## File: {file_path}\n"
            merged_content += f.read() + "\n"
            
    except UnicodeDecodeError:
        logger.warning(f"Skipping file due to encoding error: {file_path}")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        
    return merged_content


def add_merge_files(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def merge_files(
        exclude: list[str] = typer.Option(
            [], "--exclude", "-e", help="Files and directories to exclude"
        ),
        files: list[str] = typer.Option(
            [], "--file", "-f", help="Additional files to merge"
        ),
    ) -> None:
        """Merges files from a git repository and/or specified input files into a temporary file."""
        console = Console()
        merged_content = ""
        
        try:
            # Process git-tracked files first
            try:
                # files just created
                result1 = subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                # files already managed by git
                result2 = subprocess.run(
                    ["git", "ls-files"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                git_files = result1.stdout.splitlines() + result2.stdout.splitlines()
                
                console.print(f"\n[bold]Git Files:[/bold]\n{git_files}")

                # Process git-tracked files
                for file_path_str in git_files:
                    segments = file_path_str.split("/")
                    if any(seg in (IGNORED_FILES + exclude) for seg in segments):
                        logger.info(f"Ignoring file: {file_path_str}")
                        continue
                        
                    file_path = Path(".") / file_path_str
                    merged_content = process_file(file_path, merged_content, logger)

            except subprocess.CalledProcessError:
                logger.warning("Not in a git repository, processing only input files")

            # Process additional input files
            for file_path_str in files:
                file_path = Path(file_path_str)
                merged_content = process_file(file_path, merged_content, logger)

            if not merged_content:
                console.print("\n[red]Error:[/red] No files to process")
                raise typer.Exit(1)
                
            # Create temp file and open in VS Code
            temp_file = create_temp_file(
                filename="merged_files.txt",
                content=merged_content
            )
            console.print(f"\n[bold]Merged Files: [blue]{temp_file}[/blue][/bold]\n\n")
            vscode_utils.open_file_with_vscode(temp_file)
            
        except Exception as e:
            logger.error("merge_files.failed", error=str(e))
            console.print("\n[red]Error:[/red] Failed to merge files.")
            raise typer.Exit(1)