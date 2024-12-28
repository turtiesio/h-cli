import os
import subprocess
from urllib.parse import urlparse

import typer
from rich.console import Console

from app.frameworks.logger import setup_logger as get_logger
from app.tools.vscode_utils import open_file_with_vscode

logger = get_logger(__name__)


def add_git_clone(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def function(
        repo_url: str,
        target_dir: str = typer.Option(
            None,
            "--target",
            "-t",
            help="Target directory to clone into",
        ),
    ) -> None:
        """Git repository를 clone하고 VS Code에서 엽니다."""
        console = Console()

        try:
            repo_name = os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]
            if target_dir is None:
                target_dir = os.path.join(os.path.expanduser("~"), "dev", repo_name)

            console.print(
                f"\n[bold]Cloning repository:[/bold] {repo_url} to {target_dir}\n"
            )

            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)

            # Clone the repository
            process = subprocess.Popen(
                ["git", "clone", repo_url, target_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if process.stdout:
                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        console.print(output.strip())

            if process.returncode != 0:
                if process.stderr:
                    error_output = process.stderr.read()
                    logger.error("git.clone.failed", error=error_output)
                    console.print(
                        f"\n[red]Error:[/red] Failed to clone repository: {error_output}"
                    )
                else:
                    logger.error(
                        "git.clone.failed",
                        error="Git clone failed with no error message",
                    )
                    console.print(
                        f"\n[red]Error:[/red] Git clone failed with no error message"
                    )
                raise typer.Exit(1)

            console.print(
                f"\n[bold]Repository cloned successfully to:[/bold] {target_dir}\n"
            )

            # Open the cloned directory in VS Code
            open_file_with_vscode(target_dir)

        except Exception as e:
            logger.error("git.clone.failed", error=str(e))
            console.print(
                "\n[red]Error:[/red] An unexpected error occurred while cloning the repository."
            )
            raise typer.Exit(1)
