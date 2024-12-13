import typer

from h.core.commands import add_main, add_version
from h.plugins.git.functions import add_git_commit_msg_prompt, add_git_tree
from h.plugins.git.functions.git_clone import add_git_clone

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

if __name__ == "__main__":
    app()
