import os
import tempfile
from typing import Optional

from h.utils.logger import get_logger

logger = get_logger(__name__)


def create_temp_file(prefix: str, content: str) -> str:
    """임시 파일 생성.

    Args:
        prefix: 파일 이름
        content: 파일 내용

    Returns:
        생성된 임시 파일 경로
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix=prefix,
        delete=False,
        encoding="utf-8",
    ) as temp:
        temp.write(content)
        return temp.name
