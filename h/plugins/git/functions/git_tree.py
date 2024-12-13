import typer
from rich.console import Console

from h.plugins.git.commands import GitCommands
from h.plugins.git.exceptions import GitError
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger

logger = get_logger(__name__)


def add_git_tree(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def function(
        tree_depth: int = typer.Option(
            3, "--depth", "-d", help="Maximum depth for directory tree"
        ),
    ) -> None:
        """Git repository의 파일 목록 출력."""
        console = Console()

        try:
            git = GitCommands(logger)
            tree = git.get_directory_tree(tree_depth)

            console.print(f"\n[bold]Project Structure:[/bold]\n{tree}")

            # save file
            temp_file = create_temp_file("git_file_list_", tree)
            console.print(f"\n[bold]File List: [blue]{temp_file}[/blue][/bold]\n\n")
        except GitError as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
        except Exception as e:
            logger.error("git.list_files.failed", error=str(e))
            console.print(
                "\n[red]Error:[/red] 파일 목록을 가져오는 중 오류가 발생했습니다."
            )
            raise typer.Exit(1)
