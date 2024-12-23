import os
import typer
from pathlib import Path
from rich.console import Console
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger
from h.utils import vscode_utils
import subprocess

logger = get_logger(__name__)

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
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if the file is ignored by git
                    try:
                        result = subprocess.run(
                            ["git", "check-ignore", str(file_path)],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        if result.stdout.strip():
                            logger.debug(f"Ignoring file: {file_path} (git ignored)")
                            continue  # Skip the file if it's ignored by git
                    except subprocess.CalledProcessError:
                        # git check-ignore returns an error if the file is not ignored
                        pass
                    
                    if file.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".rb", ".php", ".html", ".css", ".scss", ".less", ".json", ".yaml", ".yml", ".toml", ".ini", ".txt", ".md")):
                        with open(file_path, "r") as f:
                            merged_content += f"## File: {file_path}\n"
                            merged_content += f.read() + "\n"

            temp_file = create_temp_file(
                filename="merged_files.txt", content=merged_content
            )
            console.print(f"\n[bold]Merged Files File: [blue]{temp_file}[/blue][/bold]\n\n")
            vscode_utils.open_file_with_vscode(temp_file)
        except Exception as e:
            logger.error("merge_files.failed", error=str(e))
            console.print("\n[red]Error:[/red] Failed to merge files.")
            raise typer.Exit(1)