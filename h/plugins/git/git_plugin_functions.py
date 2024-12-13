import os
import subprocess
from rich.console import Console
from h.plugins.git.exceptions import GitError
from h.plugins.git.git_commands import GitCommands
from h.utils.logger import get_logger
from h.utils.file_utils import create_temp_file
import typer

logger = get_logger(__name__)

def get_git_commands() -> GitCommands:
    """Git 명령어 실행을 위한 인스턴스 생성."""
    return GitCommands(logger)

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

def open_in_vscode(file_path: str) -> None:
    """VSCode로 파일 열기.
    
    Args:
        file_path: 파일 경로
    """
    try:
        subprocess.run(["code", file_path], check=True)
    except Exception as e:
        logger.error("git.vscode.failed", error=str(e))

def prompt(
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
) -> None:
    """커밋 메시지 생성을 위한 프롬프트 생성."""
    console = Console()

    try:
        git = get_git_commands()
        
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
        console.print(f"\n[bold]Commit Message File: [blue]{temp_file}[/blue][/bold]\n\n")
    except GitError as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("git.prompt.failed", error=str(e))
        console.print("\n[red]Error:[/red] 프롬프트 생성 중 오류가 발생했습니다.")
        raise typer.Exit(1)

def list_files() -> None:
    """List files in the git repository."""
    console = Console()
    try:
        git = get_git_commands()
        files = git.list_files_command()
        console.print("\n[bold]Git Files:[/bold]")
        console.print(files)
    except GitError as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("git.list_files.failed", error=str(e))
        console.print("\n[red]Error:[/red] 파일 목록을 가져오는 중 오류가 발생했습니다.")
        raise typer.Exit(1)