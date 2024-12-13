import typer
from rich.console import Console

from h.plugins.git.commands import GitCommands
from h.plugins.git.exceptions import GitError
from h.utils.file_utils import create_temp_file
from h.utils.logger import get_logger

logger = get_logger(__name__)


def git_commit_msg_prompt_generator(app: typer.Typer, name: str) -> None:
    @app.command(name=name)
    def function(
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
            git = GitCommands(logger)

            # 먼저 변경사항과 스테이지 상태 체크 (에러나면 여기서 종료)
            git.check_changes()

            # 이후 정보 수집
            status = git.get_status()
            diff = git.get_staged_diff()
            logs = "\n".join(git.get_recent_logs(log_count))
            tree = git.get_directory_tree(tree_depth)

            # 프롬프트 출력
            console.print(f"\n[bold]Git Status:[/bold]\n{status}")
            console.print(f"\n[bold]Staged Changes:[/bold]\n{diff}")
            console.print(f"\n[bold]Recent Commits:[/bold]\n{logs}")
            console.print(f"\n[bold]Project Structure:[/bold]\n{tree}")

            # 템플릿 파일 생성
            content = _PROMPT.format(
                status=git.get_status(),
                diff=git.get_staged_diff(),
                logs="\n".join(git.get_recent_logs(log_count)),
                tree=git.get_directory_tree(tree_depth),
            )

            temp_file = create_temp_file("git_commit_", content)
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





_PROMPT = """# Git Commit Message Generator

## Directives
TARGET OBJECTIVE:
Generate clear, consistent, and informative Git commit messages that effectively communicate code changes while following established best practices and conventional commits specification.

CONTEXT:
- Git commit message structure (subject line, body, footer)
- Conventional commits format (type, scope, description)
- Project-specific requirements
- Branch context and issue tracking

CORE INSTRUCTION:
Given a set of code changes, create a commit message that:

1. Start with a conventional commit type:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - style: Code style updates
   - refactor: Code refactoring
   - test: Test updates
   - chore: Maintenance tasks

2. Include a clear scope (optional):
   - Component name
   - Module affected
   - Feature area

3. Write a concise subject line:
   - Use imperative mood
   - Maximum 50 characters
   - No period at the end
   - Capitalize first letter

4. Provide detailed body (if needed):
   - Blank line after subject
   - Wrap at 72 characters
   - Explain "what" and "why" (not "how")
   - Reference related issues

FORMAT REQUIREMENTS:
<type>(<scope>): <subject>

[blank line]
<body>

[blank line]
<footer>

Example:
feat(auth): implement OAuth2 login flow

Implement Google OAuth2 authentication to replace 
basic auth. This change improves security and user 
experience by removing password management.

Closes #123
Breaking change: Removes basic auth endpoints

VALIDATION CHECKS:
- Verify conventional commit format
- Check character limits (50/72)
- Confirm imperative mood
- Validate issue references
- Check for breaking change notices
- Ensure clear context is provided

EXAMPLE OUTPUT:
feat(api): add user preference endpoint

Implement new REST endpoint for managing user preferences.
This addition supports the upcoming dark mode feature
and will enable future personalization options.

Resolves #456
Requires DB migration: 202312110001

OPTIMIZATION NOTES:
1. Use consistent terminology across commits
2. Reference tickets/issues when applicable
3. Highlight breaking changes prominently
4. Include relevant context for future reference
5. Consider adding co-author tags for pair programming

Write in Korean and markdown

Here is the actual git current state:

----------------------------------------------

## Git Status

{status}

## Staged Changes

{diff}

## Recent Commits

{logs}

## Project Structure

{tree}
"""
