import os
import subprocess
from typing import Any, Callable

import typer
from rich.console import Console

from h.plugins.git.commands import GitCommands
from h.plugins.git.exceptions import GitError
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger

logger = get_logger(__name__)


def get_template_content() -> str:
    """커밋 메시지 템플릿 내용 가져오기."""
    template_path = os.path.join(os.path.dirname(__file__), "git_commit_template.txt")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.error("git.template.failed", error=str(e))
        return """type(scope): summary

# Why is this change needed?
Prior to this change, 

# How does it address the issue?
This change

# Provide links to any relevant tickets, articles or other resources
References: 

Co-authored-by: """


def git_commit_msg_prompt_options(
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            kwargs["log_count"] = log_count
            kwargs["tree_depth"] = tree_depth
            return func(*args, **kwargs)

        return wrapper

    return decorator


def git_commit_msg_prompt(log_count: int = 5, tree_depth: int = 3) -> None:
    """커밋 메시지 생성을 위한 프롬프트 생성."""
    console = Console()

    try:
        git = GitCommands(logger)

        # 먼저 변경사항과 스테이지 상태 체크 (에러나면 여기서 종료)
        git.check_changes()

        # 이후 정보 수집
        status = git.get_status()
        diff = git.get_staged_diff()
        logs = "\n".join(git.get_recent_logs(log_count))
        tree = git.get_directory_tree(tree_depth)

        # 프롬프트 출력
        console.print("\n[bold]Git Status:[/bold]")
        console.print(status)

        console.print("\n[bold]Staged Changes:[/bold]")
        console.print(diff)

        console.print("\n[bold]Recent Commits:[/bold]")
        console.print(logs)

        console.print("\n[bold]Project Structure:[/bold]")
        console.print(tree)

        # 템플릿 파일 생성
        content = f"""# Git Commit Message Generator

## Directives
{get_template_content()}

## Git Status
```
{status}
```

## Staged Changes
```
{diff}
```

## Recent Commits
```
{logs}
```

## Project Structure
```
{tree}
```
"""
        temp_file = create_temp_file(content, message="Commit message file created:")

        # 파일 경로 출력
        console.print(
            f"\n[bold]Commit Message File: [blue]{temp_file}[/blue][/bold]\n\n"
        )
    except GitError as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("git.prompt.failed", error=str(e))
        console.print("\n[red]Error:[/red] 프롬프트 생성 중 오류가 발생했습니다.")
        raise typer.Exit(1)


def git_tree():
    """Git repository의 파일 목록 출력."""
    console = Console()

    try:
        files = GitCommands(logger).list_files_command()

        console.print("\n[bold]Git Files:[/bold]")
        console.print(files)

        # save file
        temp_file = create_temp_file(files, message="File list created:")
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
