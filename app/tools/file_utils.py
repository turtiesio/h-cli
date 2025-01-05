import os
import tempfile
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Union

from app.frameworks.logger import setup_logger

logger = setup_logger(__name__)


def create_temp_file(
    filename: str,
    content: str,
) -> str:
    """임시 파일 생성.
    Args:
        filename: 파일 이름
        content: 파일 내용

    Returns:
        생성된 임시 파일 경로
    """
    tempfile_path = os.path.join(tempfile.gettempdir(), filename)

    with open(tempfile_path, "w", encoding="utf-8") as temp:
        temp.write(content)

    return tempfile_path


def read_file(file_path: Union[str, Path]) -> str:
    """Read the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file(file_path: Union[str, Path], content: str) -> None:
    """Write content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def is_binary_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, "rb") as file:
            chunk = file.read(8192)
            return b"\x00" in chunk
    except Exception:
        return True


def should_exclude_file(
    file_path: Union[str, Path], exclude_patterns: List[str], include_docs: bool = False
) -> bool:
    """Check if a file should be excluded based on glob patterns and file type."""
    # Exclude .md files by default unless include_docs is True
    if not include_docs and str(file_path).endswith(".md"):
        return True

    return any(fnmatch(str(file_path), pattern) for pattern in exclude_patterns)
