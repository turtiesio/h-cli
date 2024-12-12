"""Git plugin for h-cli.

This module provides git helper commands for the h-cli tool.
It follows clean architecture principles and provides proper error handling.
"""
import os
import tempfile
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

import typer
from rich import print as rprint
from rich.tree import Tree
from rich.console import Console
import structlog

# Initialize logger
logger = structlog.get_logger()

class GitError(Exception):
    """Custom exception for git-related errors."""
    pass

class GitCommands:
    """Git command handler implementing clean architecture."""
    
    def __init__(self, logger: Any) -> None:
        """Initialize GitCommands with logger.
        
        Args:
            logger: Structured logger instance
        """
        self.logger = logger
    
    def get_status(self) -> str:
        """Get git status of current directory.
        
        Returns:
            String containing git status output
            
        Raises:
            GitError: If not in a git repository or git is not installed
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error("git.status.failed", error=str(e))
            raise GitError("Not a git repository or git not installed")

    def get_modified_contents(self) -> Dict[str, str]:
        """Get contents of modified files.
        
        Returns:
            Dict mapping file paths to their modified contents
            
        Raises:
            GitError: If git commands fail
        """
        try:
            # Get list of modified files
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip().split("\n")
            
            modified_files = {}
            for line in status:
                if not line:
                    continue
                    
                status_code = line[:2]
                file_path = line[3:].strip()
                
                # Only process modified files
                if status_code.strip() in ["M", "A", "??", " M"]:
                    try:
                        with open(file_path, "r") as f:
                            modified_files[file_path] = f.read()
                    except Exception as e:
                        self.logger.warning(
                            "git.read_file.failed",
                            file=file_path,
                            error=str(e)
                        )
                        
            return modified_files
            
        except subprocess.CalledProcessError as e:
            self.logger.error("git.modified_contents.failed", error=str(e))
            raise GitError("Failed to get modified contents")

    def get_recent_logs(self, count: int = 5) -> List[str]:
        """Get recent git commit logs.
        
        Args:
            count: Number of recent logs to retrieve
            
        Returns:
            List of recent git log messages
            
        Raises:
            GitError: If git log command fails
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--oneline"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().split("\n")
        except subprocess.CalledProcessError as e:
            self.logger.error("git.recent_logs.failed", error=str(e))
            raise GitError("Failed to get git logs")

    def get_directory_tree(self, max_depth: int = 3) -> Tree:
        """Get directory tree structure.
        
        Args:
            max_depth: Maximum depth to traverse
            
        Returns:
            Rich Tree object representing directory structure
        """
        def _add_to_tree(tree: Tree, path: Path, depth: int) -> None:
            if depth > max_depth:
                return
                
            try:
                for item in path.iterdir():
                    if item.name.startswith("."):
                        continue
                        
                    if item.is_file():
                        tree.add(f"📄 {item.name}")
                    else:
                        subtree = tree.add(f"📁 {item.name}")
                        _add_to_tree(subtree, item, depth + 1)
            except PermissionError:
                pass

        root = Path.cwd()
        tree = Tree(f"📁 {root.name}")
        _add_to_tree(tree, root, 1)
        return tree

# Create Typer app
app = typer.Typer(
    help="Git helper commands",
    name="git",
    short_help="git commands",
)

def get_git_commands() -> GitCommands:
    """Get GitCommands instance with current context.
    
    Returns:
        Configured GitCommands instance
    """
    from click import get_current_context
    ctx = get_current_context()
    return GitCommands(ctx.obj["logger"])

@app.command()
def commit(
    message: Optional[str] = typer.Option(
        None, "-m", "--message", help="Commit message"
    ),
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
) -> None:
    """Generate git commit message and commit changes.
    
    This command helps generate meaningful commit messages by showing:
    - Modified file contents
    - Recent commit history
    - Directory structure
    """
    try:
        git = get_git_commands()
        
        # Get git status
        status = git.get_status()
        if not status:
            rprint("[yellow]No changes to commit[/yellow]")
            raise typer.Exit(1)
            
        # Show modified contents
        modified = git.get_modified_contents()
        if modified:
            rprint("\n[bold]Modified Files:[/bold]")
            for file, content in modified.items():
                rprint(f"\n[green]{file}[/green]")
                rprint(content[:500] + "..." if len(content) > 500 else content)
                
        # Show recent logs
        logs = git.get_recent_logs(log_count)
        if logs:
            rprint("\n[bold]Recent Commits:[/bold]")
            for log in logs:
                rprint(f"  {log}")
                
        # Show directory tree
        tree = git.get_directory_tree(tree_depth)
        rprint("\n[bold]Directory Structure:[/bold]")
        rprint(tree)
        
        # If message provided, commit directly
        if message:
            subprocess.run(["git", "commit", "-m", message], check=True)
            rprint("[green]Changes committed successfully![/green]")
        else:
            # Open editor for commit message
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as f:
                f.write("\n\n# Modified files:\n")
                for file in modified:
                    f.write(f"# - {file}\n")
                f.flush()
                
                editor = os.environ.get("EDITOR", "vim")
                subprocess.run([editor, f.name], check=True)
                
                f.seek(0)
                commit_msg = f.read().split("\n# Modified files:")[0].strip()
                
                if commit_msg:
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                    rprint("[green]Changes committed successfully![/green]")
                else:
                    rprint("[yellow]Commit aborted - no message provided[/yellow]")
                    
    except GitError as e:
        rprint(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        rprint(f"[red]Error: Git command failed: {e.stderr.decode() if e.stderr else str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("git.commit.failed", error=str(e))
        rprint(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)

# Add command alias
app.command(name="gc")(commit)
