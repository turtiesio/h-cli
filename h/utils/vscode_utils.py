import os
import shutil
import subprocess
from typing import Optional

# editor list
editors = [
    "windsurf",
    "cursor",
    "code",
]


def find_editor() -> Optional[str]:
    """Discovers the first available VSCode-like editor."""
    # Check PATH first
    for editor in editors:
        if shutil.which(editor):
            return editor

    # Check common install locations
    common_paths = [
        os.path.expanduser("~/.windsurf-server/bin"),
        os.path.expanduser("~/.vscode/bin"),
        os.path.expanduser("~/.cursor/bin"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            for editor in editors:
                editor_path = os.path.join(path, editor)
                if os.path.exists(editor_path):
                    return editor_path

    return None


def get_vscode_sock() -> Optional[str]:
    """Get VSCode IPC socket path from env or find it."""
    if "VSCODE_IPC_HOOK_CLI" in os.environ:
        return os.environ["VSCODE_IPC_HOOK_CLI"]

    uid = os.getuid()
    try:
        # Try /tmp first
        socks = (
            subprocess.check_output(
                "find /tmp -name 'vscode-ipc-*.sock'", shell=True, text=True
            )
            .strip()
            .split("\n")
        )
        if socks and socks[0]:
            return socks[0]

        # Try /run/user if /tmp didn't work
        socks = (
            subprocess.check_output(
                f"find /run/user/{uid} -name 'vscode-ipc-*.sock'", shell=True, text=True
            )
            .strip()
            .split("\n")
        )
        if socks and socks[0]:
            return socks[0]

    except subprocess.CalledProcessError:
        pass

    return None


def setup_vscode_env() -> None:
    """Sets up environment variables needed for VSCode CLI."""
    os.environ["TERM_PROGRAM"] = "vscode"
    if sock := get_vscode_sock():
        os.environ["VSCODE_IPC_HOOK_CLI"] = sock


def open_file_with_vscode(file_path: str) -> None:
    """Opens the given file path with VS Code."""
    if not (editor := find_editor()):
        print("No VSCode-like editor found")
        return

    setup_vscode_env()

    try:
        subprocess.run([editor, file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to open file: {e}")


if __name__ == "__main__":
    open_file_with_vscode("h/utils/vscode_utils.py")
