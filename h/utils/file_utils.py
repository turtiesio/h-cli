import tempfile
import os
from typing import Optional
from h.utils.logger import get_logger

logger = get_logger(__name__)

def create_temp_file(content: str, message: Optional[str] = None) -> str:
    """임시 파일 생성.

    Args:
        content: 파일 내용
        message: 파일 경로 출력 메시지

    Returns:
        생성된 임시 파일 경로
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix="git_commit_",
        delete=False,
        encoding="utf-8",
    ) as temp:
        temp.write(content)
        if message:
            logger.info(message, path=temp.name)
        return temp.name