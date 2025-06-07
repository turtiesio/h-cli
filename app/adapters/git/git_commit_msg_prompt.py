import os
import sys
import time
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from app.adapters.ai.gemini import GeminiAI
from app.core.config import get_config
from app.frameworks.logger import setup_logger as get_logger
from app.tools.file_utils import create_temp_file
from app.tools.vscode_utils import open_file_with_vscode

from .git_commands import GitCommands, GitError

logger = get_logger(__name__)


def add_git_commit_msg_prompt(app: typer.Typer, name: str) -> None:
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

        config = get_config()

        if config.gemini_api_key is None:
            console.print("\n[red]Error:[/red] Gemini API key is not set.")
            raise typer.Exit(1)

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
            # console.print(f"\n[bold]Git Status:[/bold]\n{status}")
            # console.print(f"\n[bold]Staged Changes:[/bold]\n{diff}")
            # console.print(f"\n[bold]Recent Commits:[/bold]\n{logs}")
            # console.print(f"\n[bold]Project Structure:[/bold]\n{tree}")

            # Generate commit message using Gemini
            gemini = GeminiAI(config.gemini_api_key)
            prompt = _PROMPT.format(
                status=status,
                diff=diff,
                logs=logs,
                tree=tree,
            )

            try:
                with Live(console=console, screen=True) as live:
                    start_time = time.time()
                    spinner = Spinner(
                        "dots", text="Generating commit message...", style="bold green"
                    )
                    live.update(spinner)

                    commit_message = gemini.generate_text(prompt)
                    commit_message = commit_message.replace("`", "")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    live.update(
                        Text(
                            f"Commit message generated in {elapsed_time:.2f} seconds.",
                            style="bold green",
                        )
                    )

                console.print(f"\n[bold]Commit Message:[/bold]\n{commit_message}")

                # Construct and print the git commit command
                console.print(
                    f"\n[bold]Git Commit Command:[/bold]\n[green]{commit_message}[/green]"
                )

                escaped_message = commit_message.replace("!", "\\!")
                git_commit_command = f'git commit -m "{escaped_message}"'
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {str(e)}")
                console.print(
                    "\n[red]Error:[/red] 프롬프트 생성 중 오류가 발생했습니다."
                )
                console.print("\n[red]Error:[/red] 프롬프트를 대신 저장합니다.")
                git_commit_command = prompt

            temp_file = create_temp_file(
                filename="git_commit_msg.txt", content=git_commit_command
            )

            console.print(
                f"\n[bold]Commit Message File: [blue]{temp_file}[/blue][/bold]\n\n"
            )

            open_file_with_vscode(temp_file)
        except GitError as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
        except Exception as e:
            logger.error("git.prompt.failed", error=str(e))
            console.print("\n[red]Error:[/red] 프롬프트 생성 중 오류가 발생했습니다.")
            raise typer.Exit(1)


_PROMPT = """You are an expert in writing Conventional Commit messages. Follow the Conventional Commits specification (v1.0.0) meticulously. The commit message structure must be:

<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

**Commit Message Requirements:**

*   **Type:** MUST be one of `feat`, `fix`, `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`, `revert`.
    *   `feat`: A new feature.
    *   `fix`: A bug fix.
    *   `build`: Changes that affect the build system or external dependencies (e.g., gulp, npm, webpack).
    *   `chore`: Miscellaneous tasks that don't fit into other types.
    *   `ci`: Changes to CI configuration files and scripts.
    *   `docs`: Documentation changes.
    *   `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
    *   `refactor`: Code changes that neither fix a bug nor add a feature.
    *   `perf`: A code change that improves performance.
    *   `test`: Adding missing tests or correcting existing tests.
     *  `revert`: Reverting a previous commit.
*   **Scope:**  (Optional) A noun in parentheses describing the section of the codebase affected, e.g., `feat(api)` or `fix(parser)`.
*   **Description:** A short summary of the changes. The description MUST immediately follow the colon and space after the type/scope prefix. It should use imperative, present tense ("add feature", not "added feature" or "adds feature").
*   **Body:** (Optional) Detailed explanation of the changes. Should be separated from the description by a blank line. USE multiple paragraphs.(100 chars max)
*   **Footer:** (Optional) Can include `BREAKING CHANGE:` description of breaking changes, `Refs:` for issue/PR numbers, or other similar information. Must follow a blank line after the body and be in a `token: value` or `token #value` format.
*   **Breaking Change:** MUST use `!` after the type or scope (e.g., `feat!:` or `feat(api)!:`) or include a footer that starts with `BREAKING CHANGE:`.
*   **Imperative:** Descriptions should be in the imperative, present tense ("add feature", not "added feature" or "adds feature").
*  **Use correct capitalization:** The units of information that make up Conventional Commits MUST NOT be treated as case sensitive by implementors, with the exception of BREAKING CHANGE which MUST be uppercase.

**Examples:**

*   `feat: add user authentication`
*   `fix(auth): prevent login issues`
*  `feat(api)!: send an email to the customer when a product is shipped`
*   `docs: update README with installation instructions`
*   `chore: update dependencies`
*   `perf: optimize image loading`
*   `fix: fix a bug that was crashing the app`
*   `refactor: simplify complex code`
*   `test: add unit tests for user service`
*   `build: add webpack config`
*    `ci: update github action`
* `revert: let us never again speak of the noodle incident\n\nRefs: 676104e, a215868`

*  **Use Korean**
*  **Each line must be less than 100 characters. Use newline characters to separate paragraphs**
*  **Give me plain text instead of markdown**
*  **LINES SHOULD NOT BE LONGER THAN 100 CHARACTERS!!!!!!!!!!!**
*  **SHORT AND CONCISE RESPONSE**
*  **READABILITY IS VERY IMPORTANT**

**Recent Commits**

{logs}

**Project Structure**

{tree}

**Now, generate a conventional commit message for the following change in Korean:**

**Git Status**

{status}

**Staged Changes**

{diff}
"""
