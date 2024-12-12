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

    def get_staged_diff(self) -> str:
        """Get diff of staged changes.
        
        Returns:
            String containing git diff of staged changes
            
        Raises:
            GitError: If git command fails
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error("git.staged_diff.failed", error=str(e))
            raise GitError("Failed to get staged changes")
            
    def get_modified_contents(self) -> Dict[str, str]:
        """Get contents of modified files.
        
        Returns:
            Dict mapping file paths to their modified contents
            
        Raises:
            GitError: If git commands fail
        """
        try:
            # Get git root directory
            try:
                git_root = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()
                self.logger.info("git.root", path=git_root)
            except subprocess.CalledProcessError as e:
                self.logger.error("git.root.failed", error=str(e))
                raise GitError("Not a git repository")

            # Get list of modified files relative to git root
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=git_root,  # Run git status from root
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            
            self.logger.info("git.status", output=status)
            
            if not status:
                return {}
                
            modified_files = {}
            for line in status.split("\n"):
                if not line:
                    continue
                    
                status_code = line[:2]
                rel_path = line[3:].strip().strip('"')  # Handle quoted paths
                
                # Only process modified files
                if status_code.strip() in ["M", "A", "??", " M"]:
                    try:
                        # Ensure rel_path doesn't start with a slash
                        if rel_path.startswith("/"):
                            rel_path = rel_path[1:]
                            
                        # Use os.path.join to handle path components correctly
                        abs_path = os.path.normpath(os.path.join(git_root, rel_path))
                        self.logger.info(
                            "git.file_path",
                            rel_path=rel_path,
                            abs_path=abs_path,
                            exists=os.path.isfile(abs_path)
                        )
                        
                        if not os.path.isfile(abs_path):
                            # Try with h/ prefix if file not found
                            if not rel_path.startswith("h/"):
                                rel_path = f"h/{rel_path}"
                                abs_path = os.path.normpath(os.path.join(git_root, rel_path))
                            
                            if not os.path.isfile(abs_path):
                                self.logger.warning(
                                    "git.read_file.failed",
                                    file=rel_path,
                                    error="File not found"
                                )
                                continue
                            
                        with open(abs_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            self.logger.info(
                                "git.file_read",
                                file=rel_path,
                                content_length=len(content)
                            )
                            modified_files[rel_path] = content
                    except Exception as e:
                        self.logger.warning(
                            "git.read_file.failed",
                            file=rel_path,
                            error=str(e)
                        )
                        
            if not modified_files:
                self.logger.warning("git.no_modified_files")
                raise GitError("No modified files found")
                
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

    def get_directory_tree(self, max_depth: int = 3) -> str:
        """Get directory tree structure respecting gitignore.
        
        Args:
            max_depth: Maximum depth to traverse
            
        Returns:
            String representation of the directory tree
            
        Raises:
            GitError: If tree command fails
        """
        try:
            # Create temporary file for gitignore patterns
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.gitignore.temp', delete=False) as temp_file:
                # Get ignored files from git
                try:
                    ignored = subprocess.run(
                        ["git", "ls-files", "-oi", "--exclude-standard", "--directory"],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout.strip()
                    temp_file.write(ignored)
                    temp_file.flush()
                except subprocess.CalledProcessError:
                    self.logger.warning("git.ignored_files.failed", message="Could not get git ignored files")
                    # If git command fails, create empty file
                    pass

                # Run tree command
                try:
                    result = subprocess.run(
                        ["tree", "-I", ".git|node_modules|dist", "--prune", "-L", str(max_depth)],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return result.stdout.strip()
                except subprocess.CalledProcessError as e:
                    self.logger.error("git.tree.failed", error=str(e))
                    return "Could not generate directory tree"
                finally:
                    try:
                        os.unlink(temp_file.name)
                    except OSError:
                        pass
        except Exception as e:
            self.logger.error("git.directory_tree.failed", error=str(e))
            return "Could not generate directory tree"

def setup_git(app: typer.Typer) -> None:
    """Set up git plugin commands.
    
    Args:
        app: Typer application
    """
    app.add_typer(
        GitPlugin(),
        name="git",
        help="Git related commands",
    )


def get_git_commands() -> GitCommands:
    """Get GitCommands instance with current context.
    
    Returns:
        Configured GitCommands instance
    """
    from click import get_current_context
    ctx = get_current_context()
    return GitCommands(ctx.obj["logger"])

# Create Typer app for git commands
app = typer.Typer(name="git", help="Git helper commands")

@app.callback(invoke_without_command=True)
def default_command(
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
) -> None:
    """Git prompt helper - generates commit message template."""
    prompt(log_count=log_count, tree_depth=tree_depth)

@app.command("prompt", hidden=True)
def prompt(
    log_count: int = typer.Option(
        5, "--logs", "-l", help="Number of recent logs to show"
    ),
    tree_depth: int = typer.Option(
        3, "--depth", "-d", help="Maximum depth for directory tree"
    ),
) -> None:
    """Generate a commit message prompt based on changes.
    
    This command helps generate meaningful commit message prompts by showing:
    - Modified file contents
    - Recent commit history
    - Directory structure
    
    Args:
        log_count: Number of recent logs to display
        tree_depth: Maximum depth for directory tree display
        
    Raises:
        GitError: If git operations fail
        typer.Exit: If operation fails
    """
    console = Console()

    try:
        git = get_git_commands()
        
        # Create a temporary file with the template
        template_path = os.path.join(os.path.dirname(__file__), "git_commit_template.txt")
        if not os.path.exists(template_path):
            console.print("[yellow]Template file not found, using default template[/yellow]")
            template_path = None
            
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp:
            # Read template if exists
            template_content = ""
            if template_path:
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                except Exception as e:
                    console.print(f"[yellow]Failed to read template: {e}[/yellow]")
                    template_path = None
            
            # Get git info
            status = git.get_status()
            diff = git.get_staged_diff()
            logs = "\n".join(git.get_recent_logs(log_count))
            tree = git.get_directory_tree(tree_depth)
            
            # Replace placeholders
            content = template_content.replace("$GIT_STATUS", status)
            content = content.replace("$GIT_DIFF_CONTENT", diff)
            content = content.replace("$GIT_LOG_RECENT", logs)
            content = content.replace("$TREE_OUTPUT", tree)
            
            # Write to temp file
            temp.write(content)
            temp.flush()
            
            console.print("\nTemplate content:")
            console.print(content)
            console.print("\n")
            console.print(f"\nCreated commit message template at: [red]{temp.name}[/red]\n")

    except GitError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)
