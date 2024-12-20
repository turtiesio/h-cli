from h.config import load_config
import typer
from h.core.commands import add_main, add_version
from h.plugins.git.functions import add_git_commit_msg_prompt, add_git_tree
from h.plugins.git.functions.git_clone import add_git_clone
from h.plugins.ai.commands import add_ai

load_config()

app = typer.Typer(
    name="h",
    help="Personal productivity CLI tool",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments are provided
    context_settings={"help_option_names": ["-h", "--help"]},  # Enable -h flag
)

add_main(app, "main")
add_version(app, "version")

add_git_commit_msg_prompt(app, "gp")
add_git_tree(app, "gt")
add_git_clone(app, "gc")
add_ai(app, "ai")

if __name__ == "__main__":
    app()
