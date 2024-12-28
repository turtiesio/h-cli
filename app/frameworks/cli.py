import typer

from app.adapters.ai.commands import add_ai
from app.adapters.base.merge_files import add_merge_files
from app.adapters.git.functions import add_git_commit_msg_prompt, add_git_tree
from app.adapters.git.functions.git_clone import add_git_clone
from app.core.config import load_config
from app.core.use_cases.commands import add_main, add_version

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
add_merge_files(app, "m")

if __name__ == "__main__":
    app()
